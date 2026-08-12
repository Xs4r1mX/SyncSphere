from django.db import models

from apps.common.models.base import BaseModel
from apps.transfers.constants import TransferItemKind, TransferItemStatus


class TransferItem(BaseModel):
    """One planned folder or file step within a transfer job."""

    job = models.ForeignKey(
        "transfers.TransferJob",
        on_delete=models.CASCADE,
        related_name="items",
    )
    sequence = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=16, choices=TransferItemKind.choices)

    source_item_id = models.CharField(max_length=255)
    source_path = models.CharField(max_length=1024, blank=True, default="")
    source_name = models.CharField(max_length=512)

    dest_parent_id = models.CharField(max_length=255, blank=True, default="")
    dest_item_id = models.CharField(max_length=255, blank=True, default="")
    dest_name = models.CharField(max_length=512, blank=True, default="")

    size_bytes = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=255, blank=True, default="")

    status = models.CharField(
        max_length=32,
        choices=TransferItemStatus.choices,
        default=TransferItemStatus.PENDING,
        db_index=True,
    )
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "transfer_items"
        ordering = ("sequence", "id")
        indexes = [
            models.Index(fields=("job", "status"), name="xfer_item_job_status"),
        ]

    def __str__(self) -> str:
        return f"{self.kind}:{self.source_name} ({self.status})"
