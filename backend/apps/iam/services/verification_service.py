import datetime

from django.conf import settings
from django.utils import timezone

from apps.iam.models import EmailVerificationToken


class VerificationService:

    EXPIRY_HOURS = settings.EMAIL_VERIFICATION_EXPIRY_HOURS

    @classmethod
    def create_email_verification_token(cls, user):

        cls.invalidate_existing_tokens(user)

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


    @classmethod
    def verify_email_token(cls, token):

        verification = (
            EmailVerificationToken.objects
            .select_related("user")
            .filter(token=token)
            .first()
        )


        if not verification:
            raise ValueError(
                "Invalid verification token."
            )


        if verification.is_verified:
            raise ValueError(
                "Email is already verified."
            )


        if verification.is_expired:
            raise ValueError(
                "Verification token has expired."
            )


        user = verification.user


        user.is_verified = True
        user.save(
            update_fields=[
                "is_verified"
            ]
        )


        verification.verified_at = timezone.now()

        verification.save(
            update_fields=[
                "verified_at"
            ]
        )


        return user


    @classmethod
    def invalidate_existing_tokens(cls, user):

        EmailVerificationToken.objects.filter(
            user=user,
            verified_at__isnull=True,
            invalidated_at__isnull=True,
        ).update(
            invalidated_at=timezone.now()
        )


    @classmethod
    def regenerate_verification_token(cls, email):

        from django.contrib.auth import get_user_model

        User = get_user_model()


        user = User.objects.filter(
            email=email
        ).first()


        if not user:
            raise ValueError(
                "User not found."
            )


        if user.is_verified:
            raise ValueError(
                "Email is already verified."
            )


        token = cls.create_email_verification_token(
            user
        )


        return user, token