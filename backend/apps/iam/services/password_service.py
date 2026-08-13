from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone

from apps.activity.constants import ActivityAction, ActivityResourceType
from apps.common.events import emit_domain_event
from apps.common.exceptions.iam import (
    EmailNotVerifiedException,
    InactiveUserException,
    IncorrectPasswordException,
    InvalidPasswordResetTokenException,
    UserNotFoundException,
)
from apps.iam.models import PasswordResetToken, User
from apps.iam.services.token_service import TokenService
from apps.notification.services import EmailService


class PasswordService:

    @staticmethod
    def change_password(
        *,
        user,
        old_password,
        new_password,
    ):
        """
        Change password for authenticated user.
        """

        if not check_password(old_password, user.password):

            raise IncorrectPasswordException("Current password is incorrect.")

        if old_password == new_password:

            raise IncorrectPasswordException(
                "New password cannot be same as old password."
            )

        user.set_password(new_password)

        user.save(update_fields=["password"])

        emit_domain_event(
            action=ActivityAction.AUTH_PASSWORD_CHANGED,
            user=user,
            resource_type=ActivityResourceType.ACCOUNT,
            resource_id=str(user.uuid),
            resource_name=user.email,
            metadata={"via": "change_password"},
        )

        TokenService.logout_all_devices(user)

        return user

    @staticmethod
    @transaction.atomic
    def _create_password_reset_token(user):
        """
        Create a new password reset token.

        Any existing unused tokens are removed so
        only one active reset token exists per user.
        """

        PasswordResetToken.objects.filter(
            user=user,
            is_used=False,
        ).delete()

        expires_at = timezone.now() + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES
        )

        return PasswordResetToken.objects.create(
            user=user,
            expires_at=expires_at,
        )

    @staticmethod
    def request_password_reset(
        email: str,
    ):
        """
        Handle forgot password request.
        """

        user = User.objects.filter(email=email).first()

        if not user:
            raise UserNotFoundException()

        # Optional security check
        if not user.is_active:
            raise InactiveUserException()

        if not user.is_verified:
            raise EmailNotVerifiedException()

        reset_token = PasswordService._create_password_reset_token(user)

        PasswordService._send_password_reset_email(
            user,
            reset_token,
        )

        emit_domain_event(
            action=ActivityAction.AUTH_PASSWORD_RESET_REQUESTED,
            user=user,
            resource_type=ActivityResourceType.ACCOUNT,
            resource_id=str(user.uuid),
            resource_name=user.email,
        )

    @staticmethod
    def _send_password_reset_email(
        user,
        reset_token,
    ):
        """
        Send password reset email.
        """

        reset_url = (
            f"{settings.PASSWORD_RESET_FRONTEND_URL}" f"?token={reset_token.token}"
        )

        EmailService.send_email(
            subject="Reset your SyncSphere password",
            recipient=user.email,
            html_template=("emails/auth/reset_password.html"),
            text_template=("emails/auth/reset_password.txt"),
            context={
                "first_name": user.first_name,
                "reset_url": reset_url,
                "expiry_minutes": (settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES),
            },
        )

    @staticmethod
    def _validate_password_reset_token(
        token: str,
    ):
        """
        Validate password reset token.

        Returns:
            PasswordResetToken instance
        """

        reset_token = (
            PasswordResetToken.objects.select_related("user")
            .filter(token=token)
            .first()
        )

        if not reset_token:
            raise InvalidPasswordResetTokenException()

        if reset_token.is_used:
            raise InvalidPasswordResetTokenException(
                "Password reset token has already been used."
            )

        if reset_token.is_expired:
            raise InvalidPasswordResetTokenException(
                "Password reset token has expired."
            )

        if not reset_token.user.is_active:
            raise InactiveUserException("User account is inactive.")

        return reset_token

    @staticmethod
    @transaction.atomic
    def reset_password(
        *,
        token,
        new_password,
    ):
        """
        Reset user password using
        password reset token.
        """

        reset_token = PasswordService._validate_password_reset_token(token)

        user = reset_token.user

        # Update password
        user.set_password(new_password)

        user.save(update_fields=["password"])

        # Mark reset token as consumed
        reset_token.mark_as_used()

        emit_domain_event(
            action=ActivityAction.AUTH_PASSWORD_RESET_COMPLETED,
            user=user,
            resource_type=ActivityResourceType.ACCOUNT,
            resource_id=str(user.uuid),
            resource_name=user.email,
            metadata={"via": "password_reset"},
        )

        # Logout from all devices
        TokenService.logout_all_devices(user)

        return user
