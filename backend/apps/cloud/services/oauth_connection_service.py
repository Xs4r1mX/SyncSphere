import logging

from django.db import transaction

from apps.cloud.models import CloudConnection
from apps.cloud.providers import ProviderFactory
from apps.cloud.services.connection_service import ConnectionService
from apps.cloud.services.oauth_state_service import OAuthStateService
from apps.common.constants import ProviderType
from apps.common.exceptions import (
    InvalidProviderException,
    OAuthExchangeFailedException,
    ProviderAuthException,
    ProviderNotImplementedException,
)

logger = logging.getLogger(__name__)

_OAUTH_PROVIDERS = frozenset(
    {
        ProviderType.GOOGLE_DRIVE,
        ProviderType.DROPBOX,
        ProviderType.ONEDRIVE,
    }
)


class OAuthConnectionService:
    """Orchestrates provider OAuth connect flows."""

    @staticmethod
    def start_authorization(*, user, provider: str) -> dict[str, str]:
        OAuthConnectionService._ensure_oauth_provider(provider)

        oauth_state = OAuthStateService.create_state(user=user, provider=provider)
        adapter = ProviderFactory.get(provider)

        redirect_uri = OAuthConnectionService._redirect_uri(provider)
        authorization_url = adapter.get_authorization_url(
            state=oauth_state.state,
            redirect_uri=redirect_uri,
        )

        return {
            "authorization_url": authorization_url,
            "state": oauth_state.state,
            "provider": provider,
        }

    @staticmethod
    @transaction.atomic
    def complete_authorization(
        *,
        user,
        provider: str,
        code: str,
        state: str,
    ) -> CloudConnection:
        OAuthConnectionService._ensure_oauth_provider(provider)

        state_user = OAuthStateService.consume_state(state=state, provider=provider)
        if state_user.id != user.id:
            raise OAuthExchangeFailedException(
                "OAuth state does not belong to the authenticated user."
            )

        return OAuthConnectionService._connect_with_code(
            user=user,
            provider=provider,
            code=code,
        )

    @staticmethod
    @transaction.atomic
    def complete_authorization_from_redirect(
        *,
        provider: str,
        code: str,
        state: str,
    ) -> CloudConnection:
        OAuthConnectionService._ensure_oauth_provider(provider)
        user = OAuthStateService.consume_state(state=state, provider=provider)
        return OAuthConnectionService._connect_with_code(
            user=user,
            provider=provider,
            code=code,
        )

    @staticmethod
    def _connect_with_code(
        *,
        user,
        provider: str,
        code: str,
    ) -> CloudConnection:
        adapter = ProviderFactory.get(provider)
        redirect_uri = OAuthConnectionService._redirect_uri(provider)

        try:
            exchange_result = adapter.exchange_code(
                code=code,
                redirect_uri=redirect_uri,
            )
        except ProviderAuthException as exc:
            raise OAuthExchangeFailedException(str(exc)) from exc

        identity = exchange_result["identity"]
        quota = exchange_result.get("quota", {})

        return ConnectionService.upsert_oauth_connection(
            user=user,
            provider=provider,
            provider_account_id=identity["provider_account_id"],
            account_email=identity.get("account_email", ""),
            display_name=identity.get("display_name_hint", "Cloud Drive"),
            credentials=exchange_result["credentials"],
            scopes=exchange_result.get("scopes", []),
            quota_total_bytes=quota.get("quota_total_bytes"),
            quota_used_bytes=quota.get("quota_used_bytes"),
        )

    @staticmethod
    def _ensure_oauth_provider(provider: str) -> None:
        if provider not in ProviderType.values:
            raise InvalidProviderException()

        if provider not in _OAUTH_PROVIDERS:
            raise ProviderNotImplementedException(
                f"OAuth is not implemented for provider '{provider}' yet."
            )

    @staticmethod
    def _redirect_uri(provider: str) -> str:
        from django.conf import settings

        if provider == ProviderType.GOOGLE_DRIVE:
            return settings.GOOGLE_OAUTH_REDIRECT_URI
        if provider == ProviderType.DROPBOX:
            return settings.DROPBOX_OAUTH_REDIRECT_URI
        if provider == ProviderType.ONEDRIVE:
            return settings.ONEDRIVE_OAUTH_REDIRECT_URI

        raise InvalidProviderException()
