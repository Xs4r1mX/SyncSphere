import logging

from django.contrib.auth import get_user_model

from apps.activity.services import ActivityService
from apps.cloud.models import CloudConnection
from apps.common.events import DomainEvent

logger = logging.getLogger(__name__)
User = get_user_model()


class ActivityLogObserver:
    """Persists domain events as ActivityLog rows (fail-open)."""

    def handle(self, event: DomainEvent) -> None:
        try:
            user = User.objects.filter(id=event.user_id).first()
            if user is None:
                logger.warning(
                    "Skipping activity for missing user",
                    extra={"user_id": event.user_id, "action": event.action},
                )
                return

            connection = None
            if event.connection_id is not None:
                connection = CloudConnection.objects.filter(
                    id=event.connection_id
                ).first()

            ActivityService.record(
                user=user,
                action=event.action,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                resource_name=event.resource_name,
                connection=connection,
                provider=event.provider,
                status=event.status,
                metadata=dict(event.metadata or {}),
                request_id=event.request_id or "",
            )
        except Exception:
            logger.warning(
                "ActivityLogObserver failed",
                exc_info=True,
                extra={"action": event.action, "user_id": event.user_id},
            )
