from django.db import models


class ActivityAction(models.TextChoices):
    CONNECTION_LINKED = "connection.linked", "Connection linked"
    CONNECTION_UNLINKED = "connection.unlinked", "Connection unlinked"
    CONNECTION_DISABLED = "connection.disabled", "Connection disabled"
    CONNECTION_ENABLED = "connection.enabled", "Connection enabled"

    FILE_UPLOADED = "file.uploaded", "File uploaded"
    FILE_FOLDER_CREATED = "file.folder_created", "Folder created"
    FILE_RENAMED = "file.renamed", "File renamed"
    FILE_MOVED = "file.moved", "File moved"
    FILE_TRASHED = "file.trashed", "File trashed"
    FILE_DELETED = "file.deleted", "File deleted"
    FILE_COPIED = "file.copied", "File copied"
    FILE_RESTORED = "file.restored", "File restored"

    TRANSFER_CREATED = "transfer.created", "Transfer created"
    TRANSFER_CANCEL_REQUESTED = "transfer.cancel_requested", "Transfer cancel requested"
    TRANSFER_CANCELLED = "transfer.cancelled", "Transfer cancelled"
    TRANSFER_COMPLETED = "transfer.completed", "Transfer completed"
    TRANSFER_FAILED = "transfer.failed", "Transfer failed"

    AUTH_PASSWORD_CHANGED = "auth.password_changed", "Password changed"
    AUTH_PASSWORD_RESET_REQUESTED = (
        "auth.password_reset_requested",
        "Password reset requested",
    )
    AUTH_PASSWORD_RESET_COMPLETED = (
        "auth.password_reset_completed",
        "Password reset completed",
    )
    AUTH_EMAIL_VERIFIED = "auth.email_verified", "Email verified"
    AUTH_LOGOUT_ALL_DEVICES = "auth.logout_all_devices", "Logged out all devices"


class ActivityResourceType(models.TextChoices):
    CONNECTION = "connection", "Connection"
    FILE = "file", "File"
    FOLDER = "folder", "Folder"
    TRANSFER = "transfer", "Transfer"
    ACCOUNT = "account", "Account"


class ActivityStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


def activity_title_for_action(action: str) -> str:
    """Human-readable title for UI display."""
    try:
        return ActivityAction(action).label
    except ValueError:
        return action.replace(".", " ").replace("_", " ").strip().title()


def activity_resource_type_label(resource_type: str) -> str:
    try:
        return ActivityResourceType(resource_type).label
    except ValueError:
        return resource_type.replace("_", " ").strip().title()

