import logging
from typing import Any, Optional

from django.db import IntegrityError, transaction

from apps.activity.constants import ActivityAction, ActivityResourceType
from apps.cloud.models import CloudConnection
from apps.cloud.providers import ProviderFactory
from apps.cloud.services.credential_service import CredentialService
from apps.common.constants import ConnectionStatus, ProviderType
from apps.common.events import emit_domain_event
from apps.common.exceptions import (
    ConnectionAlreadyExistsException,
    ConnectionDisabledException,
    ConnectionNotFoundException,
    InvalidProviderException,
)

logger = logging.getLogger(__name__)


class ConnectionService:
    """Business logic for managing cloud storage connections."""

    @staticmethod
    def list_connections(*, user) -> list[CloudConnection]:
        return list(
            CloudConnection.objects.filter(user=user).order_by("-created_at")
        )

    @staticmethod
    def get_connection(*, user, connection_uuid) -> CloudConnection:
        try:
            return CloudConnection.objects.get(uuid=connection_uuid, user=user)
        except CloudConnection.DoesNotExist as exc:
            raise ConnectionNotFoundException() from exc

    @staticmethod
    @transaction.atomic
    def create_connection(
        *,
        user,
        provider: str,
        display_name: str,
        provider_account_id: str,
        account_email: str = "",
        credentials: Optional[dict[str, Any]] = None,
        scopes: Optional[list[str]] = None,
        status: str = ConnectionStatus.ACTIVE,
        quota_total_bytes: Optional[int] = None,
        quota_used_bytes: Optional[int] = None,
    ) -> CloudConnection:
        if provider not in ProviderType.values:
            raise InvalidProviderException()

        # Ensures provider is registered (stubs raise only on provider ops).
        ProviderFactory.get(provider)

        encrypted = ""
        if credentials is not None:
            encrypted = CredentialService.encrypt_payload(credentials)

        try:
            connection = CloudConnection.objects.create(
                user=user,
                provider=provider,
                display_name=display_name.strip(),
                provider_account_id=provider_account_id,
                account_email=account_email or "",
                credentials_encrypted=encrypted,
                status=status,
                scopes=scopes or [],
                quota_total_bytes=quota_total_bytes,
                quota_used_bytes=quota_used_bytes,
            )
        except IntegrityError as exc:
            raise ConnectionAlreadyExistsException() from exc

        logger.info(
            "Cloud connection created",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": provider,
            },
        )
        return connection

    @staticmethod
    @transaction.atomic
    def update_display_name(
        *,
        user,
        connection_uuid,
        display_name: str,
    ) -> CloudConnection:
        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        connection.display_name = display_name.strip()
        connection.save(update_fields=["display_name", "updated_at"])

        logger.info(
            "Cloud connection display name updated",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
            },
        )
        return connection

    @staticmethod
    @transaction.atomic
    def disable_connection(*, user, connection_uuid) -> CloudConnection:
        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )

        if connection.status == ConnectionStatus.DISABLED:
            return connection

        connection.status = ConnectionStatus.DISABLED
        connection.save(update_fields=["status", "updated_at"])

        emit_domain_event(
            action=ActivityAction.CONNECTION_DISABLED,
            user=user,
            resource_type=ActivityResourceType.CONNECTION,
            resource_id=str(connection.uuid),
            resource_name=connection.display_name,
            connection=connection,
            provider=connection.provider,
        )

        logger.info(
            "Cloud connection disabled",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
            },
        )
        return connection

    @staticmethod
    @transaction.atomic
    def enable_connection(*, user, connection_uuid) -> CloudConnection:
        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )

        if connection.status == ConnectionStatus.ACTIVE:
            return connection

        if connection.status != ConnectionStatus.DISABLED:
            raise ConnectionDisabledException(
                "Only a disabled connection can be enabled."
            )

        connection.status = ConnectionStatus.ACTIVE
        connection.save(update_fields=["status", "updated_at"])

        emit_domain_event(
            action=ActivityAction.CONNECTION_ENABLED,
            user=user,
            resource_type=ActivityResourceType.CONNECTION,
            resource_id=str(connection.uuid),
            resource_name=connection.display_name,
            connection=connection,
            provider=connection.provider,
        )

        logger.info(
            "Cloud connection enabled",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
            },
        )
        return connection

    @staticmethod
    @transaction.atomic
    def store_credentials(
        *,
        user,
        connection_uuid,
        credentials: dict[str, Any],
    ) -> CloudConnection:
        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        connection.credentials_encrypted = CredentialService.encrypt_payload(
            credentials
        )
        connection.save(update_fields=["credentials_encrypted", "updated_at"])
        return connection

    @staticmethod
    def read_credentials(*, user, connection_uuid) -> dict[str, Any]:
        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        return CredentialService.decrypt_payload(connection.credentials_encrypted)

    @staticmethod
    @transaction.atomic
    def upsert_oauth_connection(
        *,
        user,
        provider: str,
        provider_account_id: str,
        display_name: str,
        account_email: str = "",
        credentials: dict[str, Any],
        scopes: Optional[list[str]] = None,
        quota_total_bytes: Optional[int] = None,
        quota_used_bytes: Optional[int] = None,
    ) -> CloudConnection:
        if provider not in ProviderType.values:
            raise InvalidProviderException()

        ProviderFactory.get(provider)
        encrypted = CredentialService.encrypt_payload(credentials)

        connection, created = CloudConnection.objects.update_or_create(
            user=user,
            provider=provider,
            provider_account_id=provider_account_id,
            defaults={
                "display_name": display_name.strip(),
                "account_email": account_email or "",
                "credentials_encrypted": encrypted,
                "status": ConnectionStatus.ACTIVE,
                "scopes": scopes or [],
                "quota_total_bytes": quota_total_bytes,
                "quota_used_bytes": quota_used_bytes,
            },
        )

        emit_domain_event(
            action=ActivityAction.CONNECTION_LINKED,
            user=user,
            resource_type=ActivityResourceType.CONNECTION,
            resource_id=str(connection.uuid),
            resource_name=connection.display_name,
            connection=connection,
            provider=connection.provider,
            metadata={"created": created},
        )

        logger.info(
            "Cloud connection %s via OAuth",
            "created" if created else "updated",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": provider,
            },
        )
        return connection

    @staticmethod
    @transaction.atomic
    def unlink_connection(*, user, connection_uuid) -> None:
        connection = ConnectionService.get_connection(
            user=user,
            connection_uuid=connection_uuid,
        )

        if connection.has_credentials:
            try:
                credentials = CredentialService.decrypt_payload(
                    connection.credentials_encrypted
                )
                adapter = ProviderFactory.get(connection.provider)
                adapter.revoke_credentials(credentials=credentials)
            except Exception:
                logger.warning(
                    "Provider revoke failed during unlink; deleting connection anyway",
                    extra={
                        "user_id": user.id,
                        "connection_uuid": str(connection.uuid),
                        "provider": connection.provider,
                    },
                )

        connection_uuid_str = str(connection.uuid)
        provider = connection.provider
        display_name = connection.display_name

        emit_domain_event(
            action=ActivityAction.CONNECTION_UNLINKED,
            user=user,
            resource_type=ActivityResourceType.CONNECTION,
            resource_id=connection_uuid_str,
            resource_name=display_name,
            connection=connection,
            provider=provider,
        )

        connection.delete()

        logger.info(
            "Cloud connection unlinked",
            extra={
                "user_id": user.id,
                "connection_uuid": connection_uuid_str,
                "provider": provider,
            },
        )
