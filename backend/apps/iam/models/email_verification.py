import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.utils import generate_secure_token


class EmailVerificationToken(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_tokens",
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_secure_token,
        editable=False,
    )

    expires_at = models.DateTimeField()

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    invalidated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "email_verification_tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - Email Verification"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_verified(self):
        return self.verified_at is not None

    @property
    def is_invalidated(self):
        return self.invalidated_at is not None

    @property
    def is_active(self):
        return not self.is_expired and not self.is_verified and not self.is_invalidated
