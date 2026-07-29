from django.contrib.auth import get_user_model
from django.db import transaction

from .verification_service import VerificationService

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