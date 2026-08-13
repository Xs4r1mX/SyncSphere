import logging
from typing import Any

from apps.common.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


def emit_domain_event(
    *,
    action: str,
    user,
    resource_type: str,
    resource_id: str = "",
    resource_name: str = "",
    connection=None,
    provider: str = "",
    status: str = "success",
    metadata: dict[str, Any] | None = None,
    request_id: str = "",
) -> None:
    """
    Enqueue a domain event for async observer fan-out on Celery.

    Request/API threads only pay for broker enqueue; observers (activity, later
    notifications) run on a worker.
    """
    event = DomainEvent(
        action=action,
        user_id=user.id,
        resource_type=resource_type,
        resource_id=resource_id or "",
        resource_name=resource_name or "",
        connection_id=getattr(connection, "id", None),
        provider=provider or getattr(connection, "provider", "") or "",
        status=status,
        metadata=metadata or {},
        request_id=request_id or "",
    )

    try:
        from apps.common.tasks.dispatch_domain_event import dispatch_domain_event

        dispatch_domain_event.apply_async(
            kwargs={
                "event_payload": event.to_dict(),
                "user_id": event.user_id,
                "request_id": event.request_id or None,
                "operation_id": event.resource_id or None,
                "provider": event.provider or None,
            }
        )
    except Exception:
        logger.warning(
            "Failed to enqueue domain event",
            exc_info=True,
            extra={
                "action": event.action,
                "user_id": event.user_id,
                "resource_type": event.resource_type,
            },
        )
