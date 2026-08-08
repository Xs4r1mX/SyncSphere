import logging

from django.conf import settings

from apps.cloud.models import CloudConnection
from apps.cloud.services.connection_service import ConnectionService
from apps.cloud.services.token_refresh_service import TokenRefreshService
from apps.common.constants import ConnectionStatus
from apps.common.exceptions import (
    ConnectionDisabledException,
    ConnectionNotFoundException,
    FileUploadTooLargeException,
    InvalidFileOperationException,
)
from apps.files.dto import FileDownloadDTO, FileItemDTO, FileListResultDTO, QuotaSummaryDTO
from apps.files.providers import FileProviderFactory

logger = logging.getLogger(__name__)


class FileService:
    """Orchestrates file operations against connected cloud storage providers."""

    @staticmethod
    def _resolve_connection(
        *,
        user,
        connection_uuid,
    ) -> tuple[CloudConnection, dict]:
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
        return connection, credentials

    @staticmethod
    def _adapter_for(connection: CloudConnection):
        return FileProviderFactory.get(connection.provider)

    @staticmethod
    def _validate_page_size(page_size: int | None) -> int:
        if page_size is None:
            return settings.FILE_LIST_DEFAULT_PAGE_SIZE

        if page_size < 1:
            raise InvalidFileOperationException("page_size must be at least 1.")

        return min(page_size, settings.FILE_LIST_MAX_PAGE_SIZE)

    @staticmethod
    def list_items(
        *,
        user,
        connection_uuid,
        parent_id: str = "root",
        page_token: str | None = None,
        page_size: int | None = None,
        trashed: bool = False,
    ) -> FileListResultDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        resolved_page_size = FileService._validate_page_size(page_size)

        result = adapter.list_items(
            credentials=credentials,
            parent_id=parent_id,
            page_token=page_token,
            page_size=resolved_page_size,
            trashed=trashed,
        )

        logger.info(
            "Listed cloud files",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "parent_id": parent_id,
                "item_count": len(result.items),
            },
        )
        return result

    @staticmethod
    def get_item(
        *,
        user,
        connection_uuid,
        item_id: str,
    ) -> FileItemDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        return adapter.get_item(credentials=credentials, item_id=item_id)

    @staticmethod
    def create_folder(
        *,
        user,
        connection_uuid,
        name: str,
        parent_id: str = "root",
    ) -> FileItemDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        item = adapter.create_folder(
            credentials=credentials,
            name=name.strip(),
            parent_id=parent_id,
        )

        logger.info(
            "Created cloud folder",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "item_id": item.provider_item_id,
            },
        )
        return item

    @staticmethod
    def upload_file(
        *,
        user,
        connection_uuid,
        name: str,
        parent_id: str,
        content: bytes,
        content_type: str,
    ) -> FileItemDTO:
        if len(content) > settings.MAX_FILE_UPLOAD_SIZE_BYTES:
            raise FileUploadTooLargeException()

        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        item = adapter.upload_file(
            credentials=credentials,
            name=name.strip(),
            parent_id=parent_id,
            content=content,
            content_type=content_type or "application/octet-stream",
        )

        logger.info(
            "Uploaded cloud file",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "item_id": item.provider_item_id,
                "size": len(content),
            },
        )
        return item

    @staticmethod
    def download_file(
        *,
        user,
        connection_uuid,
        item_id: str,
    ) -> FileDownloadDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        return adapter.download_file(credentials=credentials, item_id=item_id)

    @staticmethod
    def update_item(
        *,
        user,
        connection_uuid,
        item_id: str,
        name: str | None = None,
        parent_id: str | None = None,
    ) -> FileItemDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        item = adapter.update_item(
            credentials=credentials,
            item_id=item_id,
            name=name.strip() if name is not None else None,
            parent_id=parent_id,
        )

        logger.info(
            "Updated cloud item",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "item_id": item_id,
            },
        )
        return item

    @staticmethod
    def delete_item(
        *,
        user,
        connection_uuid,
        item_id: str,
        permanent: bool = False,
    ) -> None:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        adapter.delete_item(
            credentials=credentials,
            item_id=item_id,
            permanent=permanent,
        )

        logger.info(
            "Deleted cloud item",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "item_id": item_id,
                "permanent": permanent,
            },
        )

    @staticmethod
    def copy_item(
        *,
        user,
        connection_uuid,
        item_id: str,
        parent_id: str,
        name: str | None = None,
    ) -> FileItemDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        item = adapter.copy_item(
            credentials=credentials,
            item_id=item_id,
            parent_id=parent_id,
            name=name.strip() if name is not None else None,
        )

        logger.info(
            "Copied cloud item",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "source_item_id": item_id,
                "dest_item_id": item.provider_item_id,
            },
        )
        return item

    @staticmethod
    def restore_item(
        *,
        user,
        connection_uuid,
        item_id: str,
    ) -> FileItemDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        item = adapter.restore_item(credentials=credentials, item_id=item_id)

        logger.info(
            "Restored cloud item",
            extra={
                "user_id": user.id,
                "connection_uuid": str(connection.uuid),
                "provider": connection.provider,
                "item_id": item_id,
            },
        )
        return item

    @staticmethod
    def get_breadcrumb(
        *,
        user,
        connection_uuid,
        item_id: str,
    ) -> list[FileItemDTO]:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        return adapter.get_breadcrumb(credentials=credentials, item_id=item_id)

    @staticmethod
    def get_quota(
        *,
        user,
        connection_uuid,
    ) -> QuotaSummaryDTO:
        connection, credentials = FileService._resolve_connection(
            user=user,
            connection_uuid=connection_uuid,
        )
        adapter = FileService._adapter_for(connection)
        return adapter.get_quota(credentials=credentials)
