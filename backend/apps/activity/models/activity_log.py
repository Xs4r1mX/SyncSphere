from django.conf import settings
from django.db import models

from apps.activity.constants import (
    ActivityAction,
    ActivityResourceType,
    ActivityStatus,
)
from apps.common.models.base import BaseModel


class ActivityLog(BaseModel):
    """User-scoped audit row for cloud, file, and transfer actions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=64, choices=ActivityAction.choices, db_index=True)
    resource_type = models.CharField(
        max_length=32,
        choices=ActivityResourceType.choices,
        db_index=True,
    )
    resource_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    resource_name = models.CharField(max_length=512, blank=True, default="")
    connection = models.ForeignKey(
        "cloud.CloudConnection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    provider = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=ActivityStatus.choices,
        default=ActivityStatus.SUCCESS,
    )
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        db_table = "activity_logs"
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("user", "created_at"),
                name="activity_user_created",
            ),
            models.Index(
                fields=("user", "action"),
                name="activity_user_action",
            ),
            models.Index(
                fields=("user", "resource_type"),
                name="activity_user_resource",
            ),
            models.Index(
                fields=("user", "connection"),
                name="activity_user_connection",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.action} ({self.resource_id})"
