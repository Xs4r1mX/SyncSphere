from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel
from apps.transfers.constants import (
    TransferConflictPolicy,
    TransferJobStatus,
    TransferOperation,
)


class TransferJob(BaseModel):
    """
    Cross-connection copy/move job.

    Source is never deleted until destination write for that item is verified.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transfer_jobs",
    )
    source_connection = models.ForeignKey(
        "cloud.CloudConnection",
        on_delete=models.CASCADE,
        related_name="source_transfer_jobs",
    )
    dest_connection = models.ForeignKey(
        "cloud.CloudConnection",
        on_delete=models.CASCADE,
        related_name="dest_transfer_jobs",
    )

    operation = models.CharField(max_length=32, choices=TransferOperation.choices)
    conflict_policy = models.CharField(
        max_length=16,
        choices=TransferConflictPolicy.choices,
        default=TransferConflictPolicy.REJECT,
    )

    source_item_id = models.CharField(max_length=255)
    source_item_name = models.CharField(max_length=512, blank=True, default="")
    source_is_folder = models.BooleanField(default=False)
    dest_parent_id = models.CharField(max_length=255, default="root")

    total_bytes = models.BigIntegerField(default=0)
    bytes_transferred = models.BigIntegerField(default=0)
    items_total = models.PositiveIntegerField(default=0)
    items_completed = models.PositiveIntegerField(default=0)
    items_failed = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=32,
        choices=TransferJobStatus.choices,
        default=TransferJobStatus.PENDING,
        db_index=True,
    )
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.TextField(blank=True, default="")

    celery_task_id = models.CharField(max_length=255, blank=True, default="")
    cancel_requested = models.BooleanField(default=False)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "transfer_jobs"
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("user", "status", "created_at"),
                name="xfer_job_user_status_created",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.operation} {self.source_item_name} ({self.status})"
