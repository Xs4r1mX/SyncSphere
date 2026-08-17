import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

from apps.cloud.providers.onedrive import OneDriveAdapter
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
from apps.common.utils import file_action_flags, guess_content_type
from apps.files.dto import FileDownloadDTO, FileItemDTO, FileListResultDTO, QuotaSummaryDTO

from .base import CloudFileAdapter

logger = logging.getLogger(__name__)

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
ONEDRIVE_FOLDER_MIME_TYPE = "application/vnd.onedrive.folder"
ROOT_ITEM_ID = "root"
ITEM_FIELDS = (
    "id,name,size,folder,file,createdDateTime,lastModifiedDateTime,"
    "webUrl,parentReference,deleted"
)


class OneDriveFileAdapter(CloudFileAdapter):
    provider_type = ProviderType.ONEDRIVE

    def __init__(self) -> None:
        self._connection_adapter = OneDriveAdapter()
        self._drive_root_ids: dict[str, str] = {}
        self._drive_ids: dict[str, str] = {}

    @staticmethod
    def _access_token(credentials: dict[str, Any]) -> str:
        token = credentials.get("access_token")
        if not token:
            raise ProviderAuthException("Missing access token for OneDrive.")
        return token

    def _handle_api_error(self, exc: urllib.error.HTTPError, *, operation: str) -> None:
        status = exc.code
        logger.warning(
            "OneDrive file operation failed",
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
        if status == 401:
            raise ProviderAuthException(
                "OneDrive authentication failed."
            ) from exc
        if status == 507:
            raise InsufficientStorageException() from exc

        body = ""
        try:
            body = exc.read().decode("utf-8").lower()
        except OSError:
            pass
        if "quota" in body or "insufficient" in body:
            raise InsufficientStorageException() from exc

        raise InvalidFileOperationException(
            "OneDrive rejected the requested file operation."
        ) from exc

    def _graph_request(
        self,
        method: str,
        path: str,
        *,
        credentials: dict[str, Any],
        body: dict[str, Any] | bytes | None = None,
        content_type: str | None = None,
        operation: str,
        raw_response: bool = False,
        accept_status: frozenset[int] | None = None,
    ) -> Any:
        access_token = self._access_token(credentials)
        url = path if path.startswith("http") else f"{GRAPH_BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = None

        if body is not None:
            if isinstance(body, bytes):
                data = body
                if content_type:
                    headers["Content-Type"] = content_type
            else:
                data = json.dumps(body).encode("utf-8")
                headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, method=method, headers=headers)

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                if raw_response:
                    return response.read()
                payload = response.read()
                if not payload:
                    return {}
                return json.loads(payload.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            allowed = accept_status or frozenset()
            if exc.code in allowed:
                if raw_response:
                    return exc.read()
                payload = exc.read()
                if not payload:
                    return {}
                return json.loads(payload.decode("utf-8"))
            self._handle_api_error(exc, operation=operation)
        except urllib.error.URLError as exc:
            logger.warning(
                "OneDrive request failed",
                extra={"provider": self.provider_type, "operation": operation},
            )
            raise InvalidFileOperationException(
                "OneDrive rejected the requested file operation."
            ) from exc

    def _fetch_preauthenticated_url(self, url: str) -> bytes:
        """Fetch bytes from a Graph-issued download URL (no Authorization header)."""
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            logger.warning(
                "OneDrive download URL fetch failed",
                extra={
                    "provider": self.provider_type,
                    "operation": "download_file_fetch",
                    "status_code": exc.code,
                },
            )
            if exc.code == 404:
                raise FileNotFoundException() from exc
            raise InvalidFileOperationException(
                "OneDrive rejected the requested file download."
            ) from exc
        except urllib.error.URLError as exc:
            logger.warning(
                "OneDrive download URL fetch failed",
                extra={"provider": self.provider_type, "operation": "download_file_fetch"},
            )
            raise InvalidFileOperationException(
                "OneDrive rejected the requested file download."
            ) from exc

    def _get_download_url(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> str:
        response = self._graph_request(
            "GET",
            f"{self._item_path(item_id)}?$select=@microsoft.graph.downloadUrl",
            credentials=credentials,
            operation="get_download_url",
        )
        download_url = response.get("@microsoft.graph.downloadUrl")
        if not download_url:
            raise InvalidFileOperationException(
                "OneDrive did not provide a download URL for this item."
            )
        return download_url

    @staticmethod
    def _cache_key(credentials: dict[str, Any]) -> str:
        token = credentials.get("access_token") or ""
        return token[:32]

    def _get_drive_root_id(self, *, credentials: dict[str, Any]) -> str:
        cache_key = self._cache_key(credentials)
        cached = self._drive_root_ids.get(cache_key)
        if cached:
            return cached

        response = self._graph_request(
            "GET",
            "/me/drive/root?$select=id",
            credentials=credentials,
            operation="get_drive_root",
        )
        root_id = response.get("id")
        if not root_id:
            raise InvalidFileOperationException(
                "OneDrive did not return a drive root identifier."
            )

        self._drive_root_ids[cache_key] = root_id
        return root_id

    def _get_drive_id(self, *, credentials: dict[str, Any]) -> str:
        cache_key = self._cache_key(credentials)
        cached = self._drive_ids.get(cache_key)
        if cached:
            return cached

        response = self._graph_request(
            "GET",
            "/me/drive?$select=id",
            credentials=credentials,
            operation="get_drive_id",
        )
        drive_id = response.get("id")
        if not drive_id:
            raise InvalidFileOperationException(
                "OneDrive did not return a drive identifier."
            )

        self._drive_ids[cache_key] = drive_id
        return drive_id

    def _build_copy_parent_reference(
        self,
        *,
        credentials: dict[str, Any],
        parent_id: str,
    ) -> dict[str, str]:
        return {
            "driveId": self._get_drive_id(credentials=credentials),
            "id": self._resolve_parent_id(
                credentials=credentials,
                parent_id=parent_id,
            ),
        }

    def _resolve_copy_source_path(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> str:
        """Shared items must be copied via the remote drive item coordinates."""
        response = self._graph_request(
            "GET",
            f"{self._item_path(item_id)}?$select=id,remoteItem",
            credentials=credentials,
            operation="resolve_copy_source",
        )
        remote_item = response.get("remoteItem") or {}
        remote_id = remote_item.get("id")
        remote_parent = remote_item.get("parentReference") or {}
        remote_drive_id = remote_parent.get("driveId")
        if remote_id and remote_drive_id:
            encoded_drive = urllib.parse.quote(remote_drive_id, safe="")
            encoded_item = urllib.parse.quote(remote_id, safe="")
            return f"/drives/{encoded_drive}/items/{encoded_item}"
        return self._item_path(item_id)

    @staticmethod
    def _monitor_url_requires_auth(monitor_url: str) -> bool:
        lowered = monitor_url.lower()
        if "tempauth=" in lowered:
            return False
        if "microsoftpersonalcontent.com" in lowered:
            return False
        return True

    def _fetch_monitor_status(
        self,
        monitor_url: str,
        *,
        credentials: dict[str, Any],
    ) -> dict[str, Any]:
        monitor_url = self._absolute_graph_url(monitor_url)
        headers: dict[str, str] = {}
        if self._monitor_url_requires_auth(monitor_url):
            headers["Authorization"] = f"Bearer {self._access_token(credentials)}"

        request = urllib.request.Request(monitor_url, method="GET", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            if not payload:
                self._handle_api_error(exc, operation="copy_item_poll")
            try:
                data = json.loads(payload.decode("utf-8"))
            except json.JSONDecodeError:
                self._handle_api_error(exc, operation="copy_item_poll")
            # tempauth monitor URLs may 401 when Authorization is sent but still
            # include the async status payload in the response body.
            if data.get("status"):
                return data
            self._handle_api_error(exc, operation="copy_item_poll")
        else:
            if not payload:
                return {}
            return json.loads(payload.decode("utf-8"))

    def _resolve_parent_id(
        self,
        *,
        credentials: dict[str, Any],
        parent_id: str,
    ) -> str:
        if parent_id == ROOT_ITEM_ID:
            return self._get_drive_root_id(credentials=credentials)
        return parent_id

    @staticmethod
    def _absolute_graph_url(url: str) -> str:
        if url.startswith("http://") or url.startswith("https://"):
            return url
        if url.startswith("/"):
            return f"{GRAPH_BASE_URL}{url}"
        return f"{GRAPH_BASE_URL}/{url}"

    def _extract_monitor_url(self, response, *, operation: str) -> str:
        monitor_url = response.headers.get("Location") or response.headers.get(
            "location"
        )
        if not monitor_url:
            raise InvalidFileOperationException(
                "OneDrive copy did not return a monitor URL."
            )
        return self._absolute_graph_url(monitor_url)

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

    def _parent_path_segment(self, parent_id: str) -> str:
        if parent_id == ROOT_ITEM_ID:
            return "root"
        return f"items/{urllib.parse.quote(parent_id, safe='')}"

    def _children_path(self, parent_id: str) -> str:
        return f"/me/drive/{self._parent_path_segment(parent_id)}/children"

    def _item_path(self, item_id: str) -> str:
        if item_id == ROOT_ITEM_ID:
            return "/me/drive/root"
        return f"/me/drive/items/{urllib.parse.quote(item_id, safe='')}"

    def _upload_path(self, parent_id: str, name: str) -> str:
        encoded_name = urllib.parse.quote(name, safe="")
        return (
            f"/me/drive/{self._parent_path_segment(parent_id)}:"
            f"/{encoded_name}:/content"
        )

    def _to_item_dto(
        self,
        payload: dict[str, Any],
        *,
        parent_id: str | None = None,
        trashed: bool = False,
    ) -> FileItemDTO:
        is_folder = "folder" in payload
        mime_type = ONEDRIVE_FOLDER_MIME_TYPE
        if not is_folder:
            file_meta = payload.get("file") or {}
            mime_type = file_meta.get("mimeType") or guess_content_type(
                payload.get("name", "")
            )

        parent_ref = payload.get("parentReference") or {}
        resolved_parent = parent_id or parent_ref.get("id")
        if resolved_parent == ROOT_ITEM_ID:
            resolved_parent = ROOT_ITEM_ID

        web_view_link = payload.get("webUrl")
        deleted = payload.get("deleted")
        is_trashed = trashed or deleted is not None
        can_open, can_download = file_action_flags(
            is_folder=is_folder,
            trashed=is_trashed,
            web_view_link=web_view_link,
        )

        return FileItemDTO(
            provider_item_id=payload["id"],
            name=payload.get("name", ""),
            mime_type=mime_type,
            is_folder=is_folder,
            parent_id=resolved_parent,
            size=self._parse_optional_int(payload.get("size")),
            created_at=self._parse_timestamp(payload.get("createdDateTime")),
            modified_at=self._parse_timestamp(payload.get("lastModifiedDateTime")),
            trashed=is_trashed,
            web_view_link=web_view_link,
            can_open=can_open,
            can_download=can_download,
        )

    def list_items(
        self,
        *,
        credentials: dict[str, Any],
        parent_id: str = ROOT_ITEM_ID,
        page_token: str | None = None,
        page_size: int = 50,
        trashed: bool = False,
    ) -> FileListResultDTO:
        if trashed:
            raise InvalidFileOperationException(
                "OneDrive does not support browsing the recycle bin via the API."
            )

        if page_token:
            path = page_token
        else:
            path = (
                f"{self._children_path(parent_id)}"
                f"?$select={ITEM_FIELDS}&$top={page_size}"
            )

        response = self._graph_request(
            "GET",
            path,
            credentials=credentials,
            operation="list_items",
        )

        items = [
            self._to_item_dto(item, parent_id=parent_id, trashed=False)
            for item in response.get("value", [])
        ]
        next_link = response.get("@odata.nextLink")
        return FileListResultDTO(items=items, next_page_token=next_link)

    def get_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO:
        if item_id == ROOT_ITEM_ID:
            return FileItemDTO(
                provider_item_id=ROOT_ITEM_ID,
                name="OneDrive",
                mime_type=ONEDRIVE_FOLDER_MIME_TYPE,
                is_folder=True,
                can_open=False,
                can_download=False,
            )

        response = self._graph_request(
            "GET",
            f"{self._item_path(item_id)}?$select={ITEM_FIELDS}",
            credentials=credentials,
            operation="get_item",
        )
        return self._to_item_dto(response)

    def create_folder(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str = ROOT_ITEM_ID,
    ) -> FileItemDTO:
        body = {
            "name": name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        response = self._graph_request(
            "POST",
            self._children_path(parent_id),
            credentials=credentials,
            body=body,
            operation="create_folder",
        )
        return self._to_item_dto(response, parent_id=parent_id)

    def upload_file(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str,
        content: bytes,
        content_type: str,
    ) -> FileItemDTO:
        response_bytes = self._graph_request(
            "PUT",
            self._upload_path(parent_id, name),
            credentials=credentials,
            body=content,
            content_type=content_type or "application/octet-stream",
            operation="upload_file",
            raw_response=True,
        )
        response = json.loads(response_bytes.decode("utf-8"))
        return self._to_item_dto(response, parent_id=parent_id)

    def download_file(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileDownloadDTO:
        metadata = self.get_item(credentials=credentials, item_id=item_id)
        if metadata.is_folder:
            raise InvalidFileOperationException("Folders cannot be downloaded.")

        download_url = self._get_download_url(
            credentials=credentials,
            item_id=item_id,
        )
        content = self._fetch_preauthenticated_url(download_url)
        content_type = metadata.mime_type or guess_content_type(metadata.name)
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
        if item.web_view_link:
            return item.web_view_link
        raise InvalidFileOperationException(
            "OneDrive did not provide a web view link for this item."
        )

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

        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if parent_id is not None:
            resolved_parent_id = self._resolve_parent_id(
                credentials=credentials,
                parent_id=parent_id,
            )
            body["parentReference"] = {"id": resolved_parent_id}

        response = self._graph_request(
            "PATCH",
            self._item_path(item_id),
            credentials=credentials,
            body=body,
            operation="update_item",
        )
        return self._to_item_dto(response, parent_id=parent_id)

    def delete_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        permanent: bool = False,
    ) -> None:
        if permanent:
            self._graph_request(
                "POST",
                f"{self._item_path(item_id)}/permanentDelete",
                credentials=credentials,
                body={},
                operation="permanent_delete_item",
            )
            return

        self._graph_request(
            "DELETE",
            self._item_path(item_id),
            credentials=credentials,
            operation="delete_item",
        )

    def copy_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        parent_id: str,
        name: str | None = None,
    ) -> FileItemDTO:
        copy_source_path = self._resolve_copy_source_path(
            credentials=credentials,
            item_id=item_id,
        )
        body: dict[str, Any] = {
            "parentReference": self._build_copy_parent_reference(
                credentials=credentials,
                parent_id=parent_id,
            ),
        }
        if name is not None:
            body["name"] = name

        access_token = self._access_token(credentials)
        url = f"{GRAPH_BASE_URL}{copy_source_path}/copy"
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                monitor_url = self._extract_monitor_url(
                    response,
                    operation="copy_item",
                )
        except urllib.error.HTTPError as exc:
            if exc.code == 202:
                monitor_url = self._absolute_graph_url(
                    exc.headers.get("Location") or exc.headers.get("location") or ""
                )
                if not monitor_url or monitor_url == GRAPH_BASE_URL:
                    raise InvalidFileOperationException(
                        "OneDrive copy did not return a monitor URL."
                    ) from exc
            else:
                self._handle_api_error(exc, operation="copy_item")
                return None  # unreachable

        copied_item_id = self._poll_copy_monitor(
            monitor_url,
            credentials=credentials,
        )
        return self.get_item(credentials=credentials, item_id=copied_item_id)

    def _poll_copy_monitor(
        self,
        monitor_url: str,
        *,
        credentials: dict[str, Any],
        timeout_seconds: int = 120,
    ) -> str:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            response = self._fetch_monitor_status(
                monitor_url,
                credentials=credentials,
            )
            status = response.get("status")
            if status == "completed":
                resource_id = response.get("resourceId")
                if resource_id:
                    return resource_id
                raise InvalidFileOperationException(
                    "OneDrive copy completed without a resource id."
                )
            if status in ("failed", "cancelled"):
                raise InvalidFileOperationException(
                    "OneDrive copy operation failed."
                )
            time.sleep(0.5)

        raise InvalidFileOperationException(
            "OneDrive copy operation timed out."
        )

    def restore_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO:
        response = self._graph_request(
            "POST",
            f"{self._item_path(item_id)}/restore",
            credentials=credentials,
            body={},
            operation="restore_item",
        )
        return self._to_item_dto(response)

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
                    name="OneDrive",
                    mime_type=ONEDRIVE_FOLDER_MIME_TYPE,
                    is_folder=True,
                )
            ]

        breadcrumb: list[FileItemDTO] = []
        current_id = item_id
        root_id = self._get_drive_root_id(credentials=credentials)

        while current_id and current_id not in {ROOT_ITEM_ID, root_id}:
            item = self.get_item(credentials=credentials, item_id=current_id)
            breadcrumb.append(item)
            current_id = item.parent_id
            if not current_id or current_id in {ROOT_ITEM_ID, root_id}:
                break

        breadcrumb.reverse()
        if not breadcrumb or breadcrumb[0].provider_item_id != ROOT_ITEM_ID:
            breadcrumb.insert(
                0,
                FileItemDTO(
                    provider_item_id=ROOT_ITEM_ID,
                    name="OneDrive",
                    mime_type=ONEDRIVE_FOLDER_MIME_TYPE,
                    is_folder=True,
                ),
            )
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
