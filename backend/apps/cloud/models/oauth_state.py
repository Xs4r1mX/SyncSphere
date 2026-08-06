from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.constants import ProviderType
from apps.common.models.base import BaseModel


class OAuthState(BaseModel):
    """
    Short-lived CSRF state for an in-progress OAuth authorization.

    Links the browser redirect back to the initiating user without
    requiring JWT on the provider callback URL.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oauth_states",
    )

    provider = models.CharField(
        max_length=32,
        choices=ProviderType.choices,
        db_index=True,
    )

    state = models.CharField(max_length=128, unique=True, db_index=True)

    expires_at = models.DateTimeField(db_index=True)

    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cloud_oauth_states"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "provider"), name="oauth_state_user_provider"),
        ]

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None
