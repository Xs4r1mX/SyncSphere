import logging

from django.db import transaction
from django.utils import timezone

from apps.cloud.services.connection_service import ConnectionService
from apps.common.constants import ConnectionStatus
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

        async_result = TransferService._enqueue(job=job, request_id=request_id)
        job.celery_task_id = async_result.id or ""
        job.save(update_fields=["celery_task_id", "updated_at"])

        logger.info(
            "Transfer job enqueued",
            extra={
                "job_uuid": str(job.uuid),
                "user_id": user.id,
                "operation": operation,
                "celery_task_id": job.celery_task_id,
                "request_id": request_id,
            },
        )
        return job

    @staticmethod
    def _enqueue(*, job: TransferJob, request_id: str | None):
        from apps.transfers.tasks.run_transfer import execute_transfer

        return execute_transfer.apply_async(
            kwargs={
                "job_uuid": str(job.uuid),
                "user_id": job.user_id,
                "request_id": request_id,
                "operation_id": str(job.uuid),
                "provider": job.source_connection.provider,
            }
        )

    @staticmethod
    def list_transfers(*, user, status: str | None = None) -> list[TransferJob]:
        qs = TransferJob.objects.filter(user=user).select_related(
            "source_connection",
            "dest_connection",
        )
        if status:
            qs = qs.filter(status=status)
        return list(qs.order_by("-created_at"))

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
        else:
            job.save(update_fields=["cancel_requested", "updated_at"])

        logger.info(
            "Transfer cancel requested",
            extra={"job_uuid": str(job.uuid), "user_id": user.id, "status": job.status},
        )
        return job
