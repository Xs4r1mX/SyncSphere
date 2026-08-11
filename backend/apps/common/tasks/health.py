from celery import shared_task

from apps.common.constants import CELERY_DEFAULT_QUEUE
from apps.common.tasks.base import StructuredTask


@shared_task(
    bind=True,
    base=StructuredTask,
    name="apps.common.tasks.health.ping",
    queue=CELERY_DEFAULT_QUEUE,
)
def ping(self, *, request_id: str | None = None) -> dict:
    """
    Lightweight smoke task used for worker health checks and tests.
    """
    return {
        "ok": True,
        "task_id": self.request.id,
        "request_id": request_id,
        "queue": CELERY_DEFAULT_QUEUE,
    }
