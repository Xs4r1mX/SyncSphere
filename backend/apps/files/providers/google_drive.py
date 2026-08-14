import io
import logging
from datetime import datetime
from typing import Any

import google.auth.exceptions
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from apps.cloud.providers.google_drive import GoogleDriveAdapter
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
from apps.common.utils import file_action_flags

from .base import CloudFileAdapter

logger = logging.getLogger(__name__)

GOOGLE_FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
FILE_FIELDS = (
    "id,name,mimeType,size,parents,createdTime,modifiedTime,trashed,webViewLink"
)


class GoogleDriveFileAdapter(CloudFileAdapter):
    provider_type = ProviderType.GOOGLE_DRIVE

    def __init__(self) -> None:
        self._connection_adapter = GoogleDriveAdapter()

    def _build_service(self, credentials: dict[str, Any]):
        google_credentials = self._connection_adapter._credentials_from_payload(
            credentials
        )
        return build(
            "drive",
            "v3",
            credentials=google_credentials,
            cache_discovery=False,
        )

    def _handle_http_error(self, exc: HttpError, *, operation: str) -> None:
        status = exc.resp.status if exc.resp else 500
        logger.warning(
            "Google Drive file operation failed",
            extra={
                "provider": self.provider_type,
                "operation": operation,
                "status_code": status,
            },
        )

        if status == 404:
            raise FileNotFoundException() from exc
        if status == 403:
            raise FilePermissionDeniedException() from exc
        if status == 409:
            raise FileConflictException() from exc
        if status == 429:
            raise ProviderRateLimitedException() from exc
        if status in (507, 403) and "storageQuota" in str(exc):
            raise InsufficientStorageException() from exc
        if status == 401:
            raise ProviderAuthException(
                "Google Drive authentication failed."
            ) from exc

        raise InvalidFileOperationException(
            "Google Drive rejected the requested file operation."
        ) from exc

    def _execute(self, request, *, operation: str):
        try:
            return request.execute()
        except HttpError as exc:
            self._handle_http_error(exc, operation=operation)
        except google.auth.exceptions.GoogleAuthError as exc:
            raise ProviderAuthException(
                "Google Drive authentication failed."
            ) from exc

    @staticmethod
    def _parse_timestamp(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _parse_optional_int(value: Any) -> int | None:
        if value in (None, ""):
            return None
        return int(value)

    def _to_item_dto(self, payload: dict[str, Any]) -> FileItemDTO:
        mime_type = payload.get("mimeType", "")
        parents = payload.get("parents") or []
        is_folder = mime_type == GOOGLE_FOLDER_MIME_TYPE
        web_view_link = payload.get("webViewLink")
        trashed = bool(payload.get("trashed"))
        can_open, can_download = file_action_flags(
            is_folder=is_folder,
            trashed=trashed,
            web_view_link=web_view_link,
        )
        return FileItemDTO(
            provider_item_id=payload["id"],
            name=payload.get("name", ""),
            mime_type=mime_type,
            is_folder=is_folder,
            parent_id=parents[0] if parents else None,
            size=self._parse_optional_int(payload.get("size")),
            created_at=self._parse_timestamp(payload.get("createdTime")),
            modified_at=self._parse_timestamp(payload.get("modifiedTime")),
            trashed=trashed,
            web_view_link=web_view_link,
            can_open=can_open,
            can_download=can_download,
        )

    def list_items(
        self,
        *,
        credentials: dict[str, Any],
        parent_id: str = "root",
        page_token: str | None = None,
        page_size: int = 50,
        trashed: bool = False,
    ) -> FileListResultDTO:
        service = self._build_service(credentials)

        if trashed:
            query = "trashed=true"
        else:
            query = f"'{parent_id}' in parents and trashed=false"

        request = service.files().list(
            q=query,
            pageSize=page_size,
            pageToken=page_token,
            fields=f"nextPageToken, files({FILE_FIELDS})",
            orderBy="folder,name",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        response = self._execute(request, operation="list_items")

        items = [self._to_item_dto(item) for item in response.get("files", [])]
        return FileListResultDTO(
            items=items,
            next_page_token=response.get("nextPageToken"),
        )

    def get_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO:
        service = self._build_service(credentials)
        request = service.files().get(
            fileId=item_id,
            fields=FILE_FIELDS,
            supportsAllDrives=True,
        )
        response = self._execute(request, operation="get_item")
        return self._to_item_dto(response)

    def create_folder(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str = "root",
    ) -> FileItemDTO:
        service = self._build_service(credentials)
        body = {
            "name": name,
            "mimeType": GOOGLE_FOLDER_MIME_TYPE,
            "parents": [parent_id],
        }
        request = service.files().create(
            body=body,
            fields=FILE_FIELDS,
            supportsAllDrives=True,
        )
        response = self._execute(request, operation="create_folder")
        return self._to_item_dto(response)

    def upload_file(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str,
        content: bytes,
        content_type: str,
    ) -> FileItemDTO:
        service = self._build_service(credentials)
        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=content_type,
            resumable=False,
        )
        body = {
            "name": name,
            "parents": [parent_id],
        }
        request = service.files().create(
            body=body,
            media_body=media,
            fields=FILE_FIELDS,
            supportsAllDrives=True,
        )
        response = self._execute(request, operation="upload_file")
        return self._to_item_dto(response)

    def download_file(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileDownloadDTO:
        service = self._build_service(credentials)
        metadata = self.get_item(credentials=credentials, item_id=item_id)

        if metadata.is_folder:
            raise InvalidFileOperationException(
                "Folders cannot be downloaded."
            )

        request = service.files().get_media(fileId=item_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            try:
                _, done = downloader.next_chunk()
            except HttpError as exc:
                self._handle_http_error(exc, operation="download_file")

        content = buffer.getvalue()
        return FileDownloadDTO(
            content=content,
            name=metadata.name,
            content_type=metadata.mime_type or "application/octet-stream",
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
        if item.web_view_link:
            return item.web_view_link
        if item.is_folder:
            return f"https://drive.google.com/drive/folders/{item_id}"
        return f"https://drive.google.com/file/d/{item_id}/view"

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

        service = self._build_service(credentials)
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name

        remove_parents = None
        if parent_id is not None:
            current = self.get_item(credentials=credentials, item_id=item_id)
            if current.parent_id and current.parent_id != parent_id:
                remove_parents = current.parent_id

        request = service.files().update(
            fileId=item_id,
            body=body or None,
            addParents=parent_id if parent_id is not None else None,
            removeParents=remove_parents,
            fields=FILE_FIELDS,
            supportsAllDrives=True,
        )
        response = self._execute(request, operation="update_item")
        return self._to_item_dto(response)

    def delete_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        permanent: bool = False,
    ) -> None:
        service = self._build_service(credentials)

        if permanent:
            request = service.files().delete(
                fileId=item_id,
                supportsAllDrives=True,
            )
            self._execute(request, operation="delete_item")
            return

        request = service.files().update(
            fileId=item_id,
            body={"trashed": True},
            supportsAllDrives=True,
        )
        self._execute(request, operation="trash_item")

    def copy_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        parent_id: str,
        name: str | None = None,
    ) -> FileItemDTO:
        service = self._build_service(credentials)
        body: dict[str, Any] = {"parents": [parent_id]}
        if name is not None:
            body["name"] = name

        request = service.files().copy(
            fileId=item_id,
            body=body,
            fields=FILE_FIELDS,
            supportsAllDrives=True,
        )
        response = self._execute(request, operation="copy_item")
        return self._to_item_dto(response)

    def restore_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO:
        service = self._build_service(credentials)
        request = service.files().update(
            fileId=item_id,
            body={"trashed": False},
            fields=FILE_FIELDS,
            supportsAllDrives=True,
        )
        response = self._execute(request, operation="restore_item")
        return self._to_item_dto(response)

    def get_breadcrumb(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> list[FileItemDTO]:
        if item_id == "root":
            return [
                FileItemDTO(
                    provider_item_id="root",
                    name="My Drive",
                    mime_type=GOOGLE_FOLDER_MIME_TYPE,
                    is_folder=True,
                )
            ]

        breadcrumb: list[FileItemDTO] = []
        current_id = item_id

        while current_id:
            item = self.get_item(credentials=credentials, item_id=current_id)
            breadcrumb.append(item)
            current_id = item.parent_id

        breadcrumb.reverse()
        return breadcrumb

    def get_quota(
        self,
        *,
        credentials: dict[str, Any],
    ) -> QuotaSummaryDTO:
        service = self._build_service(credentials)
        request = service.about().get(fields="storageQuota")
        response = self._execute(request, operation="get_quota")
        storage_quota = response.get("storageQuota", {})

        total = self._parse_optional_int(storage_quota.get("limit"))
        used = self._parse_optional_int(storage_quota.get("usage"))
        available = None
        if total is not None and used is not None:
            available = max(total - used, 0)

        return QuotaSummaryDTO(
            quota_total_bytes=total,
            quota_used_bytes=used,
            quota_available_bytes=available,
        )
