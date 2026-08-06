import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.cloud.models import OAuthState
from apps.common.constants import ProviderType
from apps.common.exceptions import (
    InvalidProviderException,
    OAuthStateExpiredException,
    OAuthStateInvalidException,
)
from apps.common.utils import generate_secure_token

logger = logging.getLogger(__name__)


class OAuthStateService:
    """Creates and validates short-lived OAuth CSRF state tokens."""

    @staticmethod
    def create_state(*, user, provider: str) -> OAuthState:
        if provider not in ProviderType.values:
            raise InvalidProviderException()

        expiry_minutes = OAuthStateService._expiry_minutes()
        state_value = generate_secure_token()

        oauth_state = OAuthState.objects.create(
            user=user,
            provider=provider,
            state=state_value,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )

        logger.info(
            "OAuth state created",
            extra={
                "user_id": user.id,
                "provider": provider,
                "oauth_state_uuid": str(oauth_state.uuid),
            },
        )
        return oauth_state

    @staticmethod
    @transaction.atomic
    def consume_state(*, state: str, provider: str):
        try:
            oauth_state = OAuthState.objects.select_for_update().get(
                state=state,
                provider=provider,
            )
        except OAuthState.DoesNotExist as exc:
            raise OAuthStateInvalidException() from exc

        if oauth_state.is_consumed:
            raise OAuthStateInvalidException("OAuth state has already been used.")

        if oauth_state.is_expired:
            raise OAuthStateExpiredException()

        oauth_state.consumed_at = timezone.now()
        oauth_state.save(update_fields=["consumed_at", "updated_at"])
        return oauth_state.user

    @staticmethod
    def _expiry_minutes() -> int:
        from django.conf import settings

        return settings.OAUTH_STATE_EXPIRY_MINUTES
