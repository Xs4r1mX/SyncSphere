from celery import shared_task

from apps.common.constants import CELERY_DEFAULT_QUEUE
from apps.common.exceptions import ProviderRateLimitedException
from apps.common.tasks.base import StructuredTask
from apps.transfers.services.transfer_executor import TransferExecutor


@shared_task(
    bind=True,
    base=StructuredTask,
    name="apps.transfers.tasks.run_transfer.execute_transfer",
    queue=CELERY_DEFAULT_QUEUE,
    autoretry_for=(ProviderRateLimitedException,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_kwargs={"max_retries": 3},
)
def execute_transfer(
    self,
    *,
    job_uuid: str,
    user_id: int | None = None,
    request_id: str | None = None,
    operation_id: str | None = None,
    provider: str | None = None,
) -> dict:
    """
    Run a transfer job safely: dest write first, source delete only after verify.
    """
    from apps.transfers.models import TransferJob

    try:
        job = TransferJob.objects.get(uuid=job_uuid)
        if self.request.id:
            job.celery_task_id = self.request.id
            job.save(update_fields=["celery_task_id", "updated_at"])
    except TransferJob.DoesNotExist:
        return {"ok": False, "error": "job_not_found", "job_uuid": job_uuid}

    job = TransferExecutor.run(job_uuid=job_uuid)
    return {
        "ok": job.status
        in (
            "success",
            "partial_success",
        ),
        "job_uuid": str(job.uuid),
        "status": job.status,
        "items_completed": job.items_completed,
        "items_failed": job.items_failed,
    }
