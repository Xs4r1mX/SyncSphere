from django.contrib.auth import get_user_model


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings


from apps.common.exceptions import (
    UserNotFoundException,
    InactiveUserException,
    EmailNotVerifiedException,
    InvalidRefreshTokenException,
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
