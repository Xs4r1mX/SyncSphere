import logging

from celery import shared_task

from apps.common.constants import CELERY_DEFAULT_QUEUE
from apps.common.events.domain_event import DomainEvent
from apps.common.events.publisher import domain_event_publisher
from apps.common.tasks.base import StructuredTask

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    base=StructuredTask,
    name="apps.common.tasks.dispatch_domain_event.dispatch_domain_event",
    queue=CELERY_DEFAULT_QUEUE,
)
def dispatch_domain_event(
    self,
    *,
    event_payload: dict,
    user_id: int | None = None,
    request_id: str | None = None,
    operation_id: str | None = None,
    provider: str | None = None,
) -> dict:
    """
    Fan out a domain event to observers on a worker (not the HTTP thread).
    """
    event = DomainEvent.from_dict(event_payload)
    domain_event_publisher.publish(event)
    return {
        "ok": True,
        "action": event.action,
        "user_id": event.user_id,
        "request_id": request_id,
    }
