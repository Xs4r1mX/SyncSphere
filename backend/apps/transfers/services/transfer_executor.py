import logging

from django.db import transaction
from django.utils import timezone

from apps.activity.constants import (
    ActivityAction,
    ActivityResourceType,
    ActivityStatus,
)
from apps.common.events import emit_domain_event
from apps.common.exceptions import (
    InsufficientStorageException,
    ProviderRateLimitedException,
    TransferSourceCleanupException,
)
from apps.common.exceptions.base import AppException
from apps.files.services import FileService
from apps.transfers.constants import (
    TransferItemKind,
    TransferItemStatus,
    TransferJobStatus,
    TransferOperation,
)
from apps.transfers.models import TransferItem, TransferJob
from apps.transfers.services.name_resolver import DestinationNameResolver
from apps.transfers.services.transfer_planner import TransferPlanner

logger = logging.getLogger(__name__)


class TransferExecutor:
    """
    Executes a transfer plan with dest-write-before-source-delete safety.

    Order per file: download → upload → verify → (move only) delete source.
    """

    @staticmethod
    def run(*, job_uuid) -> TransferJob:
        try:
            job = TransferJob.objects.select_related(
                "user",
                "source_connection",
                "dest_connection",
            ).get(uuid=job_uuid)
        except TransferJob.DoesNotExist:
            logger.error("Transfer job not found", extra={"job_uuid": str(job_uuid)})
            raise

        if job.cancel_requested and job.status == TransferJobStatus.PENDING:
            return TransferExecutor._finalize_cancelled(job)

        name_resolver = DestinationNameResolver(
            user=job.user,
            connection_uuid=job.dest_connection.uuid,
            conflict_policy=job.conflict_policy,
        )
        try:
            TransferPlanner.build_plan(job=job, name_resolver=name_resolver)
            job.refresh_from_db()
            TransferExecutor._preflight_quota(job)

            job.status = TransferJobStatus.RUNNING
            job.started_at = timezone.now()
            job.save(update_fields=["status", "started_at", "updated_at"])

            TransferExecutor._execute_items(job, name_resolver=name_resolver)
            job.refresh_from_db()
            return TransferExecutor._finalize_job(job)
        except ProviderRateLimitedException:
            raise
        except AppException as exc:
            return TransferExecutor._fail_job(job, exc)
        except Exception as exc:
            logger.exception(
                "Unexpected transfer failure",
                extra={"job_uuid": str(job.uuid)},
            )
            return TransferExecutor._fail_job(
                job,
                AppException(str(exc) or "Unexpected transfer failure."),
            )

    @staticmethod
    def _preflight_quota(job: TransferJob) -> None:
        if job.total_bytes <= 0:
            return

        quota = FileService.get_quota(
            user=job.user,
            connection_uuid=job.dest_connection.uuid,
        )
        available = quota.quota_available_bytes
        if available is not None and job.total_bytes > available:
            raise InsufficientStorageException(
                f"Destination has {available} bytes free; transfer needs {job.total_bytes}."
            )

    @staticmethod
    def _execute_items(
        job: TransferJob,
        *,
        name_resolver: DestinationNameResolver,
    ) -> None:
        # Maps source folder id -> dest folder id for nested parents.
        source_folder_to_dest: dict[str, str] = {}
        items = list(job.items.order_by("sequence", "id"))

        for item in items:
            job.refresh_from_db(fields=["cancel_requested", "status"])
            if job.cancel_requested:
                TransferExecutor._cancel_remaining(job)
                return

            try:
                TransferExecutor._execute_item(
                    job=job,
                    item=item,
                    source_folder_to_dest=source_folder_to_dest,
                    name_resolver=name_resolver,
                )
            except ProviderRateLimitedException:
                raise
            except Exception as exc:
                TransferExecutor._mark_item_failed(item, exc)
                job.items_failed += 1
                job.save(update_fields=["items_failed", "updated_at"])
                # Continue other items for all-ops; single-file ops stop via finalize.
                if job.operation in (TransferOperation.COPY, TransferOperation.MOVE):
                    return

        if job.operation in (TransferOperation.MOVE_ALL,):
            TransferExecutor._cleanup_source_folders(job, source_folder_to_dest)

    @staticmethod
    def _execute_item(
        *,
        job: TransferJob,
        item: TransferItem,
        source_folder_to_dest: dict[str, str],
        name_resolver: DestinationNameResolver,
    ) -> None:
        item.status = TransferItemStatus.RUNNING
        item.save(update_fields=["status", "updated_at"])

        dest_parent_id = TransferExecutor._resolve_dest_parent(
            job=job,
            item=item,
            source_folder_to_dest=source_folder_to_dest,
        )

        if item.kind == TransferItemKind.FOLDER:
            TransferExecutor._create_dest_folder(
                job=job,
                item=item,
                dest_parent_id=dest_parent_id,
                source_folder_to_dest=source_folder_to_dest,
                name_resolver=name_resolver,
            )
            return

        TransferExecutor._transfer_file(
            job=job,
            item=item,
            dest_parent_id=dest_parent_id,
            name_resolver=name_resolver,
        )

    @staticmethod
    def _resolve_dest_parent(
        *,
        job: TransferJob,
        item: TransferItem,
        source_folder_to_dest: dict[str, str],
    ) -> str:
        # Nested items store parent source folder id in dest_parent_id until mapped.
        if item.dest_parent_id in source_folder_to_dest:
            return source_folder_to_dest[item.dest_parent_id]
        return item.dest_parent_id

    @staticmethod
    def _create_dest_folder(
        *,
        job: TransferJob,
        item: TransferItem,
        dest_parent_id: str,
        source_folder_to_dest: dict[str, str],
        name_resolver: DestinationNameResolver,
    ) -> None:
        name = item.dest_name or item.source_name
        if item.sequence != 0:
            name = name_resolver.resolve(
                parent_id=dest_parent_id,
                desired_name=item.source_name,
            )
        else:
            # Planner already reserved the root name on this resolver.
            name_resolver.remember(parent_id=dest_parent_id, name=name)

        created = FileService.create_folder(
            user=job.user,
            connection_uuid=job.dest_connection.uuid,
            name=name,
            parent_id=dest_parent_id,
            emit_event=False,
        )

        # Verify destination folder exists before any source cleanup.
        verified = FileService.get_item(
            user=job.user,
            connection_uuid=job.dest_connection.uuid,
            item_id=created.provider_item_id,
        )

        item.dest_item_id = verified.provider_item_id
        item.dest_name = verified.name
        item.dest_parent_id = dest_parent_id
        item.status = TransferItemStatus.SUCCESS
        item.save(
            update_fields=[
                "dest_item_id",
                "dest_name",
                "dest_parent_id",
                "status",
                "updated_at",
            ]
        )
        source_folder_to_dest[item.source_item_id] = verified.provider_item_id
        # Brand-new dest folder has no children yet — avoid listing it per child file.
        name_resolver.seed_empty(parent_id=verified.provider_item_id)
        job.items_completed += 1
        job.save(update_fields=["items_completed", "updated_at"])

    @staticmethod
    def _transfer_file(
        *,
        job: TransferJob,
        item: TransferItem,
        dest_parent_id: str,
        name_resolver: DestinationNameResolver,
    ) -> None:
        download = FileService.download_file(
            user=job.user,
            connection_uuid=job.source_connection.uuid,
            item_id=item.source_item_id,
        )

        dest_name = item.dest_name or item.source_name
        # Root single-file already resolved in planner; nested files resolve now.
        if item.sequence != 0:
            dest_name = name_resolver.resolve(
                parent_id=dest_parent_id,
                desired_name=item.source_name,
            )
        else:
            name_resolver.remember(parent_id=dest_parent_id, name=dest_name)

        uploaded = FileService.upload_file(
            user=job.user,
            connection_uuid=job.dest_connection.uuid,
            name=dest_name,
            parent_id=dest_parent_id,
            content=download.content,
            content_type=download.content_type or item.mime_type or "application/octet-stream",
            emit_event=False,
        )

        # Verify destination before any source mutation.
        verified = FileService.get_item(
            user=job.user,
            connection_uuid=job.dest_connection.uuid,
            item_id=uploaded.provider_item_id,
        )

        item.dest_item_id = verified.provider_item_id
        item.dest_name = verified.name
        item.dest_parent_id = dest_parent_id
        item.status = TransferItemStatus.SUCCESS
        item.save(
            update_fields=[
                "dest_item_id",
                "dest_name",
                "dest_parent_id",
                "status",
                "updated_at",
            ]
        )

        job.bytes_transferred += item.size_bytes or len(download.content)
        job.items_completed += 1
        job.save(
            update_fields=["bytes_transferred", "items_completed", "updated_at"]
        )

        if job.operation in (TransferOperation.MOVE, TransferOperation.MOVE_ALL):
            TransferExecutor._delete_source_after_success(job=job, item=item)

    @staticmethod
    def _delete_source_after_success(*, job: TransferJob, item: TransferItem) -> None:
        """Delete source only after destination write is verified."""
        try:
            FileService.delete_item(
                user=job.user,
                connection_uuid=job.source_connection.uuid,
                item_id=item.source_item_id,
                permanent=True,
                emit_event=False,
            )
        except Exception as exc:
            logger.warning(
                "Source cleanup failed after successful destination write",
                extra={
                    "job_uuid": str(job.uuid),
                    "item_uuid": str(item.uuid),
                    "source_item_id": item.source_item_id,
                    "dest_item_id": item.dest_item_id,
                    "failure_reason": exc.__class__.__name__,
                },
            )
            item.error_code = "source_cleanup_failed"
            item.error_message = str(
                TransferSourceCleanupException(
                    "Destination write succeeded but source cleanup failed."
                )
            )
            item.save(update_fields=["error_code", "error_message", "updated_at"])

    @staticmethod
    def _cleanup_source_folders(
        job: TransferJob,
        source_folder_to_dest: dict[str, str],
    ) -> None:
        """
        After move_all file deletes, remove source folders bottom-up
        only when all child items under that folder succeeded.
        """
        folder_items = list(
            job.items.filter(kind=TransferItemKind.FOLDER).order_by("-sequence")
        )
        for folder in folder_items:
            if job.cancel_requested:
                return
            descendants_failed = job.items.filter(
                source_path__startswith=f"{folder.source_path}/",
                status=TransferItemStatus.FAILED,
            ).exists()
            if descendants_failed or folder.status != TransferItemStatus.SUCCESS:
                continue
            try:
                FileService.delete_item(
                    user=job.user,
                    connection_uuid=job.source_connection.uuid,
                    item_id=folder.source_item_id,
                    permanent=True,
                    emit_event=False,
                )
            except Exception as exc:
                logger.warning(
                    "Source folder cleanup failed",
                    extra={
                        "job_uuid": str(job.uuid),
                        "source_item_id": folder.source_item_id,
                        "failure_reason": exc.__class__.__name__,
                    },
                )

    @staticmethod
    def _mark_item_failed(item: TransferItem, exc: Exception) -> None:
        item.status = TransferItemStatus.FAILED
        item.error_code = exc.__class__.__name__
        item.error_message = str(exc)
        item.save(
            update_fields=["status", "error_code", "error_message", "updated_at"]
        )

    @staticmethod
    def _cancel_remaining(job: TransferJob) -> None:
        job.items.filter(status=TransferItemStatus.PENDING).update(
            status=TransferItemStatus.CANCELLED,
            updated_at=timezone.now(),
        )

    @staticmethod
    @transaction.atomic
    def _finalize_job(job: TransferJob) -> TransferJob:
        job.refresh_from_db()
        if job.cancel_requested and job.items.filter(
            status=TransferItemStatus.CANCELLED
        ).exists():
            completed = job.items.filter(status=TransferItemStatus.SUCCESS).count()
            job.status = (
                TransferJobStatus.PARTIAL_SUCCESS
                if completed
                else TransferJobStatus.CANCELLED
            )
        elif job.items_failed and job.items_completed:
            job.status = TransferJobStatus.PARTIAL_SUCCESS
        elif job.items_failed and not job.items_completed:
            job.status = TransferJobStatus.FAILED
            if not job.error_message:
                first = job.items.filter(status=TransferItemStatus.FAILED).first()
                if first:
                    job.error_code = first.error_code
                    job.error_message = first.error_message
        else:
            job.status = TransferJobStatus.SUCCESS

        job.finished_at = timezone.now()
        job.save(
            update_fields=[
                "status",
                "error_code",
                "error_message",
                "finished_at",
                "updated_at",
            ]
        )
        TransferExecutor._emit_terminal_event(job)
        return job

    @staticmethod
    def _finalize_cancelled(job: TransferJob) -> TransferJob:
        job.status = TransferJobStatus.CANCELLED
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at", "updated_at"])
        TransferExecutor._emit_terminal_event(job)
        return job

    @staticmethod
    def _fail_job(job: TransferJob, exc: AppException) -> TransferJob:
        job.status = TransferJobStatus.FAILED
        job.error_code = exc.__class__.__name__
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save(
            update_fields=[
                "status",
                "error_code",
                "error_message",
                "finished_at",
                "updated_at",
            ]
        )
        TransferExecutor._emit_terminal_event(job)
        return job

    @staticmethod
    def _emit_terminal_event(job: TransferJob) -> None:
        if job.status == TransferJobStatus.CANCELLED:
            action = ActivityAction.TRANSFER_CANCELLED
            status = ActivityStatus.SUCCESS
        elif job.status in (
            TransferJobStatus.SUCCESS,
            TransferJobStatus.PARTIAL_SUCCESS,
        ):
            action = ActivityAction.TRANSFER_COMPLETED
            status = ActivityStatus.SUCCESS
        else:
            action = ActivityAction.TRANSFER_FAILED
            status = ActivityStatus.FAILED

        emit_domain_event(
            action=action,
            user=job.user,
            resource_type=ActivityResourceType.TRANSFER,
            resource_id=str(job.uuid),
            resource_name=job.source_item_name or job.source_item_id,
            connection=job.source_connection,
            provider=job.source_connection.provider,
            status=status,
            metadata={
                "operation": job.operation,
                "job_status": job.status,
                "items_completed": job.items_completed,
                "items_failed": job.items_failed,
                "items_total": job.items_total,
                "bytes_transferred": job.bytes_transferred,
                "error_code": job.error_code,
                "dest_connection_uuid": str(job.dest_connection.uuid),
            },
        )
