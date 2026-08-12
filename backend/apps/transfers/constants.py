from django.db import models


class TransferOperation(models.TextChoices):
    COPY = "copy", "Copy"
    MOVE = "move", "Move"
    COPY_ALL = "copy_all", "Copy all"
    MOVE_ALL = "move_all", "Move all"


class TransferConflictPolicy(models.TextChoices):
    REJECT = "reject", "Reject"
    RENAME = "rename", "Rename"


class TransferJobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PLANNING = "planning", "Planning"
    RUNNING = "running", "Running"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    PARTIAL_SUCCESS = "partial_success", "Partial success"


class TransferItemKind(models.TextChoices):
    FILE = "file", "File"
    FOLDER = "folder", "Folder"


class TransferItemStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    SKIPPED = "skipped", "Skipped"
    CANCELLED = "cancelled", "Cancelled"
