from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.utils import generate_secure_token


class PasswordResetToken(models.Model):
    """
    Stores one-time password reset tokens.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )

    token = models.CharField(
        max_length=64,
        unique=True,
        default=generate_secure_token,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False,
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        db_table = "reset_password_token"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "token",
                ]
            ),
            models.Index(
                fields=[
                    "user",
                    "is_used",
                ]
            ),
            models.Index(
                fields=[
                    "expires_at",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.user.email}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.used_at = timezone.now()

        self.save(
            update_fields=[
                "is_used",
                "used_at",
            ]
        )
