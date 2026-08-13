import logging
from datetime import datetime
from typing import Any

from apps.activity.constants import ActivityStatus
from apps.activity.models import ActivityLog
from apps.common.exceptions import ActivityNotFoundException

logger = logging.getLogger(__name__)

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100


class ActivityService:
    """Persistence and read APIs for activity logs."""

    @staticmethod
    def record(
        *,
        user,
        action: str,
        resource_type: str,
        resource_id: str = "",
        resource_name: str = "",
        connection=None,
        provider: str = "",
        status: str = ActivityStatus.SUCCESS,
        metadata: dict[str, Any] | None = None,
        request_id: str = "",
    ) -> ActivityLog | None:
        try:
            return ActivityLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id or "",
                resource_name=resource_name or "",
                connection=connection,
                provider=provider or (getattr(connection, "provider", "") or ""),
                status=status or ActivityStatus.SUCCESS,
                metadata=metadata or {},
                request_id=request_id or "",
            )
        except Exception:
            logger.warning(
                "Failed to persist activity log",
                exc_info=True,
                extra={
                    "user_id": getattr(user, "id", None),
                    "action": action,
                    "resource_type": resource_type,
                },
            )
            return None

    @staticmethod
    def list_activity(
        *,
        user,
        action: str | None = None,
        resource_type: str | None = None,
        connection_uuid=None,
        provider: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        resolved_limit = ActivityService._clamp_limit(limit)
        resolved_offset = max(0, offset)

        qs = ActivityLog.objects.filter(user=user).select_related("connection")
        if action:
            qs = qs.filter(action=action)
        if resource_type:
            qs = qs.filter(resource_type=resource_type)
        if connection_uuid:
            qs = qs.filter(connection__uuid=connection_uuid)
        if provider:
            qs = qs.filter(provider=provider)
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
    def get_activity(*, user, activity_uuid) -> ActivityLog:
        try:
            return ActivityLog.objects.select_related("connection").get(
                uuid=activity_uuid,
                user=user,
            )
        except ActivityLog.DoesNotExist as exc:
            raise ActivityNotFoundException() from exc

    @staticmethod
    def _clamp_limit(limit: int) -> int:
        if limit < 1:
            return DEFAULT_PAGE_LIMIT
        return min(limit, MAX_PAGE_LIMIT)
