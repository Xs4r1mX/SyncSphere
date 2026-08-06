import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cloud.models import CloudConnection
from apps.cloud.providers import ProviderFactory
from apps.cloud.services.credential_service import CredentialService
from apps.common.constants import ConnectionStatus
from apps.common.exceptions import ConnectionExpiredException, ProviderAuthException

logger = logging.getLogger(__name__)


class TokenRefreshService:
    """Keeps provider credentials valid and updates stored tokens."""

    @staticmethod
    def credentials_need_refresh(credentials: dict[str, Any]) -> bool:
        token_expiry = credentials.get("token_expiry")
        if not token_expiry:
            return not credentials.get("access_token")

        expiry = datetime.fromisoformat(token_expiry)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=dt_timezone.utc)

        return expiry <= timezone.now() + timedelta(minutes=2)

    @staticmethod
    @transaction.atomic
    def ensure_valid_credentials(
        *,
        connection: CloudConnection,
    ) -> dict[str, Any]:
        credentials = CredentialService.decrypt_payload(
            connection.credentials_encrypted
        )

        if not TokenRefreshService.credentials_need_refresh(credentials):
            return credentials

        return TokenRefreshService.refresh_connection(connection=connection)

    @staticmethod
    def refresh_connection(*, connection: CloudConnection) -> dict[str, Any]:
        connection = CloudConnection.objects.get(pk=connection.pk)
        credentials = CredentialService.decrypt_payload(
            connection.credentials_encrypted
        )
        refresh_token = credentials.get("refresh_token")

        if not refresh_token:
            TokenRefreshService._mark_connection(
                connection,
                status=ConnectionStatus.EXPIRED,
            )
            raise ConnectionExpiredException(
                "Refresh token is missing for this connection."
            )

        adapter = ProviderFactory.get(connection.provider)

        try:
            refreshed = adapter.refresh_access_token(refresh_token=refresh_token)
        except ProviderAuthException:
            TokenRefreshService._mark_connection(
                connection,
                status=ConnectionStatus.EXPIRED,
            )
            raise

        with transaction.atomic():
            connection = CloudConnection.objects.select_for_update().get(
                pk=connection.pk
            )
            merged = {**credentials, **refreshed}
            connection.credentials_encrypted = CredentialService.encrypt_payload(
                merged
            )
            connection.status = ConnectionStatus.ACTIVE
            connection.save(
                update_fields=["credentials_encrypted", "status", "updated_at"]
            )

        logger.info(
            "Cloud connection credentials refreshed",
            extra={
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "user_id": connection.user_id,
            },
        )
        return merged

    @staticmethod
    def _mark_connection(connection: CloudConnection, *, status: str) -> None:
        connection.status = status
        connection.save(update_fields=["status", "updated_at"])
