from django.conf import settings
from django.db import models

from apps.common.constants import ConnectionStatus, ProviderType
from apps.common.models.base import BaseModel


class CloudConnection(BaseModel):
    """
    A user's linked cloud storage account.

    Multiple accounts from the same provider are allowed when
    provider_account_id differs (e.g. Drive1, Drive2).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cloud_connections",
    )

    provider = models.CharField(
        max_length=32,
        choices=ProviderType.choices,
        db_index=True,
    )

    display_name = models.CharField(max_length=150)

    provider_account_id = models.CharField(max_length=255)

    account_email = models.EmailField(blank=True, default="")

    credentials_encrypted = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=32,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.PENDING,
        db_index=True,
    )

    scopes = models.JSONField(default=list, blank=True)

    quota_total_bytes = models.BigIntegerField(null=True, blank=True)

    quota_used_bytes = models.BigIntegerField(null=True, blank=True)

    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cloud_connections"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "provider", "provider_account_id"),
                name="uniq_user_provider_account",
            ),
        ]
        indexes = [
            models.Index(
                fields=("user", "provider", "status"),
                name="cloud_conn_user_prov_status",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.provider})"

    @property
    def has_credentials(self) -> bool:
        return bool(self.credentials_encrypted)
