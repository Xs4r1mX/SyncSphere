from django.contrib.auth import get_user_model
from django.db import transaction

from django.contrib.auth import authenticate
from django.utils import timezone


from .verification_service import VerificationService
from apps.notification.services import EmailService

from apps.common.exceptions import (
    IncorrectPasswordException,
    UserNotFoundException,
    InactiveUserException,
    EmailNotVerifiedException,
)

User = get_user_model()


class AuthService:

    @staticmethod
    @transaction.atomic
    def register_user(
        *,
        email,
        first_name,
        last_name,
        password,
    ):
        """
        Register a new user.

        Responsibilities:
        - Create user
        - Generate username (handled by UserManager/User model)
        - Hash password (handled by UserManager)
        - Send verification email (later)
        """

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        verification_token = VerificationService.create_email_verification_token(
            user=user
        )

        VerificationService.send_verification_email(
            user=user, verification_token=verification_token
        )

        return user

    @staticmethod
    def authenticate_user(*, email, password):
        """
        Authenticate user credentials
        and validate account state.
        """

        if User.objects.filter(email=email).exists() is False:
            raise UserNotFoundException()

        user = authenticate(username=email, password=password)

        if not user:

            raise IncorrectPasswordException()

        if not user.is_active:

            raise InactiveUserException()

        if not user.is_verified:

            raise EmailNotVerifiedException()

        return user

    @staticmethod
    def send_login_email(*, user, ip_address=None, login_time=None):
        """
        Send login notification email for a successful authentication.

        This method delegates to the notification EmailService which will
        ultimately call the provider to send the message.
        """

        login_time = login_time or timezone.now()

        EmailService.send_email(
            subject="New sign-in to your SyncSphere account",
            recipient=user.email,
            html_template=("emails/auth/login.html"),
            text_template=("emails/auth/login.txt"),
            context={
                "first_name": user.first_name,
                "login_time": login_time,
                "ip_address": ip_address,
            },
        )
