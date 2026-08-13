from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.activity.constants import ActivityAction, ActivityResourceType
from apps.common.events import emit_domain_event
from apps.common.exceptions import (
    EmailNotVerifiedException,
    InactiveUserException,
    InvalidRefreshTokenException,
    UserNotFoundException,
)

User = get_user_model()


class TokenService:

    @staticmethod
    def _get_refresh_token(refresh_token: str):
        """
        Validate and return a refresh token object.
        """

        try:

            refresh = RefreshToken(refresh_token)

        except TokenError:

            raise InvalidRefreshTokenException()

        return refresh

    @staticmethod
    def _get_user_from_refresh_token(
        refresh: RefreshToken,
    ):
        """
        Get user associated with refresh token.
        """

        user_id = refresh.get(api_settings.USER_ID_CLAIM)

        if not user_id:
            raise UserNotFoundException("User information missing from token.")

        try:

            user = User.objects.get(pk=user_id)

        except User.DoesNotExist:

            raise UserNotFoundException()

        return user

    @staticmethod
    def generate_tokens(user):

        refresh = RefreshToken.for_user(user)

        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    @staticmethod
    def refresh_token_pair(token: str):
        """
        Validate old refresh token,
        create new token pair,
        and blacklist old refresh token.
        """

        # 1. Convert raw token string
        # into RefreshToken object

        refresh = TokenService._get_refresh_token(token)

        # 2. Get user from token

        user = TokenService._get_user_from_refresh_token(refresh)

        # 3. Validate user state

        if not user.is_active:

            raise InactiveUserException()

        if not user.is_verified:

            raise EmailNotVerifiedException()

        # 4. Create new token pair

        new_tokens = TokenService.generate_tokens(user)

        # 5. Blacklist old refresh token

        TokenService.blacklist_refresh_token(refresh)

        return new_tokens

    @staticmethod
    def blacklist_refresh_token(refresh: RefreshToken):
        """
        Blacklist a refresh token.
        """

        refresh.blacklist()

    @staticmethod
    def logout(refresh_token: str):
        """
        Blacklist refresh token.
        """

        refresh = TokenService._get_refresh_token(refresh_token)

        TokenService.blacklist_refresh_token(refresh)

    @staticmethod
    @transaction.atomic
    def logout_all_devices(user):
        """
        Logout user from all devices by
        blacklisting every outstanding
        refresh token.
        """

        outstanding_tokens = OutstandingToken.objects.filter(user=user)

        for token in outstanding_tokens:

            BlacklistedToken.objects.get_or_create(token=token)

        emit_domain_event(
            action=ActivityAction.AUTH_LOGOUT_ALL_DEVICES,
            user=user,
            resource_type=ActivityResourceType.ACCOUNT,
            resource_id=str(user.uuid),
            resource_name=getattr(user, "email", "") or "",
        )
