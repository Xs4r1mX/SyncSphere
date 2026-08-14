import logging
from datetime import datetime
from typing import Any

import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import FileMetadata, FolderMetadata, WriteMode

from apps.cloud.providers.dropbox import DropboxAdapter
from apps.common.constants import ProviderType
from apps.common.exceptions import (
    FileConflictException,
    FileNotFoundException,
    FilePermissionDeniedException,
    InsufficientStorageException,
    InvalidFileOperationException,
    ProviderAuthException,
    ProviderRateLimitedException,
)
from apps.files.dto import FileDownloadDTO, FileItemDTO, FileListResultDTO, QuotaSummaryDTO
from apps.common.utils import file_action_flags, guess_content_type

from .base import CloudFileAdapter

logger = logging.getLogger(__name__)

DROPBOX_FOLDER_MIME_TYPE = "application/vnd.dropbox.folder"
ROOT_ITEM_ID = "root"


def _dropbox_preview_url(url: str) -> str:
    """Prefer Dropbox web preview over direct download (?dl=0)."""
    if "dl=" in url:
        return url.replace("dl=1", "dl=0")
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}dl=0"


class DropboxFileAdapter(CloudFileAdapter):
    provider_type = ProviderType.DROPBOX

    def __init__(self) -> None:
        self._connection_adapter = DropboxAdapter()

    def _build_client(self, credentials: dict[str, Any]) -> dropbox.Dropbox:
        return self._connection_adapter._client_from_payload(credentials)

    @staticmethod
    def _strip_id_prefix(item_id: str) -> str:
        if item_id.startswith("id:"):
            return item_id[3:]
        return item_id

    @staticmethod
    def _to_api_ref(item_id: str) -> str:
        if item_id == ROOT_ITEM_ID:
            return ""
        if item_id.startswith("id:"):
            return item_id
        return f"id:{item_id}"

    def _handle_api_error(self, exc: Exception, *, operation: str) -> None:
        logger.warning(
            "Dropbox file operation failed",
            extra={
                "provider": self.provider_type,
                "operation": operation,
                "error": exc.__class__.__name__,
            },
        )

        if isinstance(exc, AuthError):
            raise ProviderAuthException(
                "Dropbox authentication failed."
            ) from exc

        if isinstance(exc, ApiError):
            error = exc.error
            summary = str(error).lower()

            if hasattr(error, "is_not_found") and error.is_not_found():
                raise FileNotFoundException() from exc
            if "insufficient_space" in summary:
                raise InsufficientStorageException() from exc
            if "conflict" in summary:
                raise FileConflictException() from exc
            if hasattr(error, "is_rate_limit") and error.is_rate_limit():
                raise ProviderRateLimitedException() from exc
            if "too_many_requests" in summary:
                raise ProviderRateLimitedException() from exc
            if hasattr(error, "is_access") and error.is_access():
                raise FilePermissionDeniedException() from exc
            if "permission" in summary:
                raise FilePermissionDeniedException() from exc

        raise InvalidFileOperationException(
            "Dropbox rejected the requested file operation."
        ) from exc

    def _call(self, client: dropbox.Dropbox, operation: str, func):
        try:
            return func()
        except (ApiError, AuthError) as exc:
            self._handle_api_error(exc, operation=operation)

    @staticmethod
    def _parse_timestamp(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.now().astimezone().tzinfo)
        return value

    def _metadata_to_dto(
        self,
        metadata: FileMetadata | FolderMetadata,
        *,
        parent_id: str | None = None,
        trashed: bool = False,
    ) -> FileItemDTO:
        is_folder = isinstance(metadata, FolderMetadata)
        item_id = self._strip_id_prefix(metadata.id)
        resolved_parent = parent_id
        if resolved_parent is None:
            path_display = getattr(metadata, "path_display", "") or ""
            if path_display.count("/") <= 1:
                resolved_parent = ROOT_ITEM_ID
            else:
                resolved_parent = None

        modified_at = None
        if isinstance(metadata, FileMetadata):
            modified_at = self._parse_timestamp(metadata.server_modified)

        can_open, can_download = file_action_flags(
            is_folder=is_folder,
            trashed=trashed,
            web_view_link=None,
        )

        return FileItemDTO(
            provider_item_id=item_id,
            name=metadata.name,
            mime_type=(
                DROPBOX_FOLDER_MIME_TYPE
                if is_folder
                else guess_content_type(metadata.name)
            ),
            is_folder=is_folder,
            parent_id=resolved_parent,
            size=metadata.size if isinstance(metadata, FileMetadata) else None,
            created_at=None,
            modified_at=modified_at,
            trashed=trashed,
            web_view_link=None,
            can_open=can_open,
            can_download=can_download,
        )

    def _resolve_parent_path(
        self,
        client: dropbox.Dropbox,
        parent_id: str,
    ) -> str:
        if parent_id == ROOT_ITEM_ID:
            return ""
        metadata = self._call(
            client,
            "resolve_parent_path",
            lambda: client.files_get_metadata(self._to_api_ref(parent_id)),
        )
        return metadata.path_display

    def _build_child_path(self, parent_path: str, name: str) -> str:
        if not parent_path:
            return f"/{name}"
        return f"{parent_path.rstrip('/')}/{name}"

    def list_items(
        self,
        *,
        credentials: dict[str, Any],
        parent_id: str = ROOT_ITEM_ID,
        page_token: str | None = None,
        page_size: int = 50,
        trashed: bool = False,
    ) -> FileListResultDTO:
        client = self._build_client(credentials)

        if page_token:
            result = self._call(
                client,
                "list_items",
                lambda: client.files_list_folder_continue(page_token),
            )
        else:
            result = self._call(
                client,
                "list_items",
                lambda: client.files_list_folder(
                    self._to_api_ref(parent_id),
                    limit=page_size,
                    include_deleted=trashed,
                ),
            )

        items: list[FileItemDTO] = []
        for entry in result.entries:
            if trashed:
                if entry.__class__.__name__ != "DeletedMetadata":
                    continue
                items.append(
                    FileItemDTO(
                        provider_item_id=self._strip_id_prefix(entry.id),
                        name=getattr(entry, "name", ""),
                        mime_type="application/octet-stream",
                        is_folder=False,
                        parent_id=parent_id,
                        trashed=True,
                        can_open=False,
                        can_download=False,
                    )
                )
                continue

            if entry.__class__.__name__ == "DeletedMetadata":
                continue

            if isinstance(entry, (FileMetadata, FolderMetadata)):
                items.append(
                    self._metadata_to_dto(entry, parent_id=parent_id, trashed=False)
                )

        next_page_token = result.cursor if result.has_more else None
        return FileListResultDTO(items=items, next_page_token=next_page_token)

    def get_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO:
        if item_id == ROOT_ITEM_ID:
            return FileItemDTO(
                provider_item_id=ROOT_ITEM_ID,
                name="Dropbox",
                mime_type=DROPBOX_FOLDER_MIME_TYPE,
                is_folder=True,
                can_open=False,
                can_download=False,
            )

        client = self._build_client(credentials)
        metadata = self._call(
            client,
            "get_item",
            lambda: client.files_get_metadata(self._to_api_ref(item_id)),
        )

        if metadata.__class__.__name__ == "DeletedMetadata":
            return FileItemDTO(
                provider_item_id=self._strip_id_prefix(metadata.id),
                name=getattr(metadata, "name", ""),
                mime_type="application/octet-stream",
                is_folder=False,
                trashed=True,
                can_open=False,
                can_download=False,
            )

        if not isinstance(metadata, (FileMetadata, FolderMetadata)):
            raise FileNotFoundException()

        parent_id = ROOT_ITEM_ID
        path_display = getattr(metadata, "path_display", "") or ""
        if path_display.count("/") > 1:
            parent_path = path_display.rsplit("/", 1)[0] or ""
            if parent_path:
                parent_meta = self._call(
                    client,
                    "get_item",
                    lambda: client.files_get_metadata(parent_path),
                )
                parent_id = self._strip_id_prefix(parent_meta.id)

        return self._metadata_to_dto(metadata, parent_id=parent_id)

    def create_folder(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str = ROOT_ITEM_ID,
    ) -> FileItemDTO:
        client = self._build_client(credentials)
        parent_path = self._resolve_parent_path(client, parent_id)
        folder_path = self._build_child_path(parent_path, name)

        metadata = self._call(
            client,
            "create_folder",
            lambda: client.files_create_folder_v2(folder_path).metadata,
        )
        return self._metadata_to_dto(metadata, parent_id=parent_id)

    def upload_file(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str,
        content: bytes,
        content_type: str,
    ) -> FileItemDTO:
        client = self._build_client(credentials)
        parent_path = self._resolve_parent_path(client, parent_id)
        file_path = self._build_child_path(parent_path, name)

        metadata = self._call(
            client,
            "upload_file",
            lambda: client.files_upload(
                content,
                file_path,
                mode=WriteMode("add"),
                mute=True,
            ),
        )
        return self._metadata_to_dto(metadata, parent_id=parent_id)

    def download_file(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileDownloadDTO:
        metadata = self.get_item(credentials=credentials, item_id=item_id)
        if metadata.is_folder:
            raise InvalidFileOperationException("Folders cannot be downloaded.")

        client = self._build_client(credentials)
        _, response = self._call(
            client,
            "download_file",
            lambda: client.files_download(self._to_api_ref(item_id)),
        )
        content = response.content
        content_type = guess_content_type(metadata.name)
        return FileDownloadDTO(
            content=content,
            name=metadata.name,
            content_type=content_type,
            size=len(content),
        )

    def get_open_link(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> str:
        item = self.get_item(credentials=credentials, item_id=item_id)
        if not item.can_open:
            raise InvalidFileOperationException(
                "This item cannot be opened in the browser."
            )

        client = self._build_client(credentials)
        path = self._call(
            client,
            "get_open_link",
            lambda: client.files_get_metadata(self._to_api_ref(item_id)),
        ).path_display

        shared_links = self._call(
            client,
            "get_open_link",
            lambda: client.sharing_list_shared_links(path=path).links,
        )

        if shared_links:
            url = shared_links[0].url
        else:
            created = self._call(
                client,
                "get_open_link",
                lambda: client.sharing_create_shared_link_with_settings(path),
            )
            url = created.url

        return _dropbox_preview_url(url)

    def update_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        name: str | None = None,
        parent_id: str | None = None,
    ) -> FileItemDTO:
        if name is None and parent_id is None:
            raise InvalidFileOperationException(
                "At least one of name or parent_id must be provided."
            )

        client = self._build_client(credentials)
        current = self.get_item(credentials=credentials, item_id=item_id)
        current_path = self._call(
            client,
            "update_item",
            lambda: client.files_get_metadata(self._to_api_ref(item_id)),
        ).path_display

        if parent_id is not None:
            dest_parent_path = self._resolve_parent_path(client, parent_id)
            dest_name = name if name is not None else current.name
            dest_path = self._build_child_path(dest_parent_path, dest_name)
        elif name is not None:
            parent_path = current_path.rsplit("/", 1)[0] if "/" in current_path else ""
            dest_path = self._build_child_path(parent_path, name)
            parent_id = current.parent_id
        else:
            dest_path = current_path
            parent_id = current.parent_id

        metadata = self._call(
            client,
            "update_item",
            lambda: client.files_move_v2(current_path, dest_path).metadata,
        )
        return self._metadata_to_dto(
            metadata,
            parent_id=parent_id or current.parent_id,
        )

    def delete_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        permanent: bool = False,
    ) -> None:
        client = self._build_client(credentials)
        api_ref = self._to_api_ref(item_id)
        self._call(
            client,
            "delete_item",
            lambda: client.files_delete_v2(api_ref),
        )

    def copy_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        parent_id: str,
        name: str | None = None,
    ) -> FileItemDTO:
        client = self._build_client(credentials)
        source = self._call(
            client,
            "copy_item",
            lambda: client.files_get_metadata(self._to_api_ref(item_id)),
        )
        dest_parent_path = self._resolve_parent_path(client, parent_id)
        dest_name = name if name is not None else source.name
        dest_path = self._build_child_path(dest_parent_path, dest_name)

        metadata = self._call(
            client,
            "copy_item",
            lambda: client.files_copy_v2(source.path_display, dest_path).metadata,
        )
        return self._metadata_to_dto(metadata, parent_id=parent_id)

    def restore_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO:
        client = self._build_client(credentials)
        metadata = self._call(
            client,
            "restore_item",
            lambda: client.files_restore(self._to_api_ref(item_id), None).metadata,
        )
        return self._metadata_to_dto(metadata)

    def get_breadcrumb(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> list[FileItemDTO]:
        if item_id == ROOT_ITEM_ID:
            return [
                FileItemDTO(
                    provider_item_id=ROOT_ITEM_ID,
                    name="Dropbox",
                    mime_type=DROPBOX_FOLDER_MIME_TYPE,
                    is_folder=True,
                )
            ]

        client = self._build_client(credentials)
        metadata = self._call(
            client,
            "get_breadcrumb",
            lambda: client.files_get_metadata(self._to_api_ref(item_id)),
        )
        path_display = getattr(metadata, "path_display", "") or ""
        parts = [part for part in path_display.strip("/").split("/") if part]

        breadcrumb: list[FileItemDTO] = [
            FileItemDTO(
                provider_item_id=ROOT_ITEM_ID,
                name="Dropbox",
                mime_type=DROPBOX_FOLDER_MIME_TYPE,
                is_folder=True,
            )
        ]

        cumulative = ""
        for part in parts:
            cumulative = f"{cumulative}/{part}"
            segment_meta = self._call(
                client,
                "get_breadcrumb",
                lambda path=cumulative: client.files_get_metadata(path),
            )
            breadcrumb.append(self._metadata_to_dto(segment_meta))

        return breadcrumb

    def get_quota(
        self,
        *,
        credentials: dict[str, Any],
    ) -> QuotaSummaryDTO:
        quota = self._connection_adapter.get_quota(credentials=credentials)
        total = quota.get("quota_total_bytes")
        used = quota.get("quota_used_bytes")
        available = None
        if total is not None and used is not None:
            available = max(total - used, 0)

        return QuotaSummaryDTO(
            quota_total_bytes=total,
            quota_used_bytes=used,
            quota_available_bytes=available,
        )
