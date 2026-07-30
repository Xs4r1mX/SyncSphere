from django.contrib.auth import get_user_model
from django.db import transaction

from django.contrib.auth import authenticate


from .verification_service import VerificationService

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

        return user, verification_token

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
