import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cloud.models import CloudConnection
from apps.cloud.providers import ProviderFactory
from apps.cloud.services.token_refresh_service import TokenRefreshService
from apps.common.constants import ConnectionStatus
from apps.common.exceptions import (
    ConnectionDisabledException,
    ConnectionNotFoundException,
    ProviderAuthException,
)

logger = logging.getLogger(__name__)


class ConnectionHealthService:
    """Validates live provider connectivity and refreshes connection metadata."""

    @staticmethod
    def check_health(*, user, connection_uuid) -> dict[str, Any]:
        from apps.cloud.services.connection_service import ConnectionService

        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )

        if connection.status == ConnectionStatus.DISABLED:
            raise ConnectionDisabledException()

        if not connection.has_credentials:
            raise ConnectionNotFoundException(
                "Connection has no stored credentials."
            )

        credentials = TokenRefreshService.ensure_valid_credentials(
            connection=connection
        )
        adapter = ProviderFactory.get(connection.provider)

        try:
            identity = adapter.get_account_identity(credentials=credentials)
            quota = adapter.get_quota(credentials=credentials)
        except ProviderAuthException:
            connection.status = ConnectionStatus.ERROR
            connection.save(update_fields=["status", "updated_at"])
            raise

        connection = ConnectionHealthService._update_connection_metadata(
            connection=connection,
            identity=identity,
            quota=quota,
        )

        return {
            "uuid": str(connection.uuid),
            "status": connection.status,
            "provider": connection.provider,
            "display_name": connection.display_name,
            "account_email": connection.account_email,
            "quota_total_bytes": connection.quota_total_bytes,
            "quota_used_bytes": connection.quota_used_bytes,
            "last_synced_at": connection.last_synced_at,
            "is_healthy": connection.status == ConnectionStatus.ACTIVE,
        }

    @staticmethod
    @transaction.atomic
    def _update_connection_metadata(
        *,
        connection: CloudConnection,
        identity: dict[str, Any],
        quota: dict[str, Any],
    ) -> CloudConnection:
        connection.account_email = identity.get(
            "account_email",
            connection.account_email,
        )
        connection.quota_total_bytes = quota.get("quota_total_bytes")
        connection.quota_used_bytes = quota.get("quota_used_bytes")
        connection.status = ConnectionStatus.ACTIVE
        connection.last_synced_at = timezone.now()
        connection.save(
            update_fields=[
                "account_email",
                "quota_total_bytes",
                "quota_used_bytes",
                "status",
                "last_synced_at",
                "updated_at",
            ]
        )
        return connection
