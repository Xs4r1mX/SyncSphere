import logging
from datetime import datetime
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.activity.constants import (
    ActivityAction,
    ActivityResourceType,
    ActivityStatus,
)
from apps.cloud.services.connection_service import ConnectionService
from apps.common.constants import ConnectionStatus
from apps.common.events import emit_domain_event
from apps.common.exceptions import (
    ConnectionDisabledException,
    TransferInvalidStateException,
    TransferNotFoundException,
)
from apps.transfers.constants import (
    TransferConflictPolicy,
    TransferJobStatus,
    TransferOperation,
)
from apps.transfers.models import TransferJob

logger = logging.getLogger(__name__)

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100


class TransferService:
    """API-facing orchestration for transfer jobs."""

    @staticmethod
    @transaction.atomic
    def create_transfer(
        *,
        user,
        operation: str,
        source_connection_uuid,
        dest_connection_uuid,
        source_item_id: str,
        dest_parent_id: str = "root",
        conflict_policy: str = TransferConflictPolicy.REJECT,
        request_id: str | None = None,
    ) -> TransferJob:
        if operation not in TransferOperation.values:
            raise TransferInvalidStateException("Unsupported transfer operation.")

        if conflict_policy not in TransferConflictPolicy.values:
            raise TransferInvalidStateException("Unsupported conflict policy.")

        source = ConnectionService.get_connection(
            user=user,
            connection_uuid=source_connection_uuid,
        )
        dest = ConnectionService.get_connection(
            user=user,
            connection_uuid=dest_connection_uuid,
        )

        if source.status == ConnectionStatus.DISABLED:
            raise ConnectionDisabledException("Source connection is disabled.")
        if dest.status == ConnectionStatus.DISABLED:
            raise ConnectionDisabledException("Destination connection is disabled.")

        job = TransferJob.objects.create(
            user=user,
            source_connection=source,
            dest_connection=dest,
            operation=operation,
            conflict_policy=conflict_policy,
            source_item_id=source_item_id,
            dest_parent_id=dest_parent_id or "root",
            status=TransferJobStatus.PENDING,
        )

        job_uuid = str(job.uuid)

        def enqueue_after_commit() -> None:
            async_result = TransferService._enqueue(
                job_uuid=job_uuid,
                user_id=job.user_id,
                request_id=request_id,
                provider=source.provider,
            )
            TransferJob.objects.filter(uuid=job_uuid).update(
                celery_task_id=async_result.id or "",
            )

        transaction.on_commit(enqueue_after_commit)

        emit_domain_event(
            action=ActivityAction.TRANSFER_CREATED,
            user=user,
            resource_type=ActivityResourceType.TRANSFER,
            resource_id=str(job.uuid),
            resource_name=job.source_item_name or job.source_item_id,
            connection=source,
            provider=source.provider,
            request_id=request_id or "",
            metadata={
                "operation": operation,
                "conflict_policy": conflict_policy,
                "dest_connection_uuid": str(dest.uuid),
                "source_item_id": source_item_id,
            },
        )

        logger.info(
            "Transfer job enqueued",
            extra={
                "job_uuid": str(job.uuid),
                "user_id": user.id,
                "operation": operation,
                "request_id": request_id,
            },
        )
        return job

    @staticmethod
    def _enqueue(
        *,
        job_uuid: str,
        user_id: int,
        request_id: str | None,
        provider: str,
    ):
        from apps.transfers.tasks.run_transfer import execute_transfer

        return execute_transfer.apply_async(
            kwargs={
                "job_uuid": job_uuid,
                "user_id": user_id,
                "request_id": request_id,
                "operation_id": job_uuid,
                "provider": provider,
            }
        )

    @staticmethod
    def list_transfers(
        *,
        user,
        status: str | None = None,
        source_connection_uuid=None,
        dest_connection_uuid=None,
        operation: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        resolved_limit = TransferService._clamp_limit(limit)
        resolved_offset = max(0, offset)

        qs = TransferJob.objects.filter(user=user).select_related(
            "source_connection",
            "dest_connection",
        )
        if status:
            qs = qs.filter(status=status)
        if source_connection_uuid:
            qs = qs.filter(source_connection__uuid=source_connection_uuid)
        if dest_connection_uuid:
            qs = qs.filter(dest_connection__uuid=dest_connection_uuid)
        if operation:
            qs = qs.filter(operation=operation)
        if created_after:
            qs = qs.filter(created_at__gte=created_after)
        if created_before:
            qs = qs.filter(created_at__lte=created_before)

        qs = qs.order_by("-created_at")
        total = qs.count()
        items = list(qs[resolved_offset : resolved_offset + resolved_limit])
        return {
            "items": items,
            "limit": resolved_limit,
            "offset": resolved_offset,
            "total": total,
        }

    @staticmethod
    def get_transfer(*, user, job_uuid) -> TransferJob:
        try:
            return TransferJob.objects.select_related(
                "source_connection",
                "dest_connection",
            ).get(uuid=job_uuid, user=user)
        except TransferJob.DoesNotExist as exc:
            raise TransferNotFoundException() from exc

    @staticmethod
    def list_items(*, user, job_uuid):
        job = TransferService.get_transfer(user=user, job_uuid=job_uuid)
        return list(job.items.order_by("sequence", "id"))

    @staticmethod
    @transaction.atomic
    def cancel_transfer(*, user, job_uuid) -> TransferJob:
        try:
            job = (
                TransferJob.objects.select_for_update()
                .select_related("source_connection", "dest_connection")
                .get(uuid=job_uuid, user=user)
            )
        except TransferJob.DoesNotExist as exc:
            raise TransferNotFoundException() from exc

        if job.status in (
            TransferJobStatus.SUCCESS,
            TransferJobStatus.FAILED,
            TransferJobStatus.CANCELLED,
            TransferJobStatus.PARTIAL_SUCCESS,
        ):
            raise TransferInvalidStateException(
                "Completed transfers cannot be cancelled."
            )

        job.cancel_requested = True
        if job.status == TransferJobStatus.PENDING:
            job.status = TransferJobStatus.CANCELLED
            job.finished_at = timezone.now()
            job.save(
                update_fields=[
                    "cancel_requested",
                    "status",
                    "finished_at",
                    "updated_at",
                ]
            )
            action = ActivityAction.TRANSFER_CANCELLED
            event_status = ActivityStatus.SUCCESS
        else:
            job.save(update_fields=["cancel_requested", "updated_at"])
            action = ActivityAction.TRANSFER_CANCEL_REQUESTED
            event_status = ActivityStatus.SUCCESS

        emit_domain_event(
            action=action,
            user=user,
            resource_type=ActivityResourceType.TRANSFER,
            resource_id=str(job.uuid),
            resource_name=job.source_item_name or job.source_item_id,
            connection=job.source_connection,
            provider=job.source_connection.provider,
            status=event_status,
            metadata={
                "operation": job.operation,
                "job_status": job.status,
            },
        )

        logger.info(
            "Transfer cancel requested",
            extra={"job_uuid": str(job.uuid), "user_id": user.id, "status": job.status},
        )
        return job

    @staticmethod
    def _clamp_limit(limit: int) -> int:
        if limit < 1:
            return DEFAULT_PAGE_LIMIT
        return min(limit, MAX_PAGE_LIMIT)
