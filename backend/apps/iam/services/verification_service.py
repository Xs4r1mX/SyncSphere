import datetime

from django.conf import settings
from django.utils import timezone

from apps.iam.models import EmailVerificationToken


class VerificationService:

    EXPIRY_HOURS = settings.EMAIL_VERIFICATION_EXPIRY_HOURS

    @classmethod
    def create_email_verification_token(cls, user):

        expires_at = (
            timezone.now()
            + datetime.timedelta(
                hours=cls.EXPIRY_HOURS
            )
        )

        verification_token = (
            EmailVerificationToken.objects.create(
                user=user,
                expires_at=expires_at,
            )
        )

        return verification_token