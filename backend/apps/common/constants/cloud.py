from django.db import models


class ProviderType(models.TextChoices):
    GOOGLE_DRIVE = "google_drive", "Google Drive"
    DROPBOX = "dropbox", "Dropbox"
    ONEDRIVE = "onedrive", "OneDrive"


class ConnectionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    DISABLED = "disabled", "Disabled"
    EXPIRED = "expired", "Expired"
    ERROR = "error", "Error"
