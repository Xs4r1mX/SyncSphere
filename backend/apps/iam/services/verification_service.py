import datetime

from django.conf import settings
from django.utils import timezone

from apps.iam.models import EmailVerificationToken

from apps.common.exceptions import (
    InvalidVerificationTokenException,
    VerificationTokenExpiredException,
    EmailAlreadyVerifiedException,
    UserNotFoundException,
)
from apps.notification.services import EmailService


class VerificationService:

    EXPIRY_HOURS = settings.EMAIL_VERIFICATION_EXPIRY_HOURS

    @classmethod
    def create_email_verification_token(cls, user):

        cls.invalidate_existing_tokens(user)

        expires_at = timezone.now() + datetime.timedelta(hours=cls.EXPIRY_HOURS)

        verification_token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=expires_at,
        )

        return verification_token

    @classmethod
    def send_verification_email(cls, user, verification_token):
        """
        Send email verification message to the user.

        Mirrors the behavior of the password reset email sender: builds
        a frontend verification URL and calls the notification EmailService
        to send the templated message.
        """

        verification_url = f"{settings.EMAIL_VERIFICATION_FRONTEND_URL}?token={verification_token.token}"

        EmailService.send_email(
            subject="Verify your SyncSphere account",
            recipient=user.email,
            html_template=("emails/auth/verify_email.html"),
            text_template=("emails/auth/verify_email.txt"),
            context={
                "first_name": user.first_name,
                "verification_url": verification_url,
                "expiry_hours": (settings.EMAIL_VERIFICATION_EXPIRY_HOURS),
            },
        )

    @classmethod
    def verify_email_token(cls, token):

        verification = (
            EmailVerificationToken.objects.select_related("user")
            .filter(token=token)
            .first()
        )

        if not verification or verification.is_invalidated:
            raise InvalidVerificationTokenException()

        if verification.is_verified:
            raise EmailAlreadyVerifiedException()

        if verification.is_expired:
            raise VerificationTokenExpiredException()

        user = verification.user

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        verification.verified_at = timezone.now()

        verification.save(update_fields=["verified_at"])

        return user

    @classmethod
    def invalidate_existing_tokens(cls, user):

        EmailVerificationToken.objects.filter(
            user=user,
            verified_at__isnull=True,
            invalidated_at__isnull=True,
        ).update(invalidated_at=timezone.now())

    @classmethod
    def regenerate_verification_token(cls, email):

        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.filter(email=email).first()

        if not user:
            raise UserNotFoundException()

        if user.is_verified:
            raise EmailAlreadyVerifiedException()

        token = cls.create_email_verification_token(user)

        return user, token
