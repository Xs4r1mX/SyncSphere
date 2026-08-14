from abc import ABC, abstractmethod
from typing import Any

from apps.files.dto import FileDownloadDTO, FileItemDTO, FileListResultDTO, QuotaSummaryDTO


class CloudFileAdapter(ABC):
    """Provider-specific file and folder operations."""

    provider_type: str

    @abstractmethod
    def list_items(
        self,
        *,
        credentials: dict[str, Any],
        parent_id: str = "root",
        page_token: str | None = None,
        page_size: int = 50,
        trashed: bool = False,
    ) -> FileListResultDTO: ...

    @abstractmethod
    def get_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO: ...

    @abstractmethod
    def create_folder(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str = "root",
    ) -> FileItemDTO: ...

    @abstractmethod
    def upload_file(
        self,
        *,
        credentials: dict[str, Any],
        name: str,
        parent_id: str,
        content: bytes,
        content_type: str,
    ) -> FileItemDTO: ...

    @abstractmethod
    def download_file(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileDownloadDTO: ...

    @abstractmethod
    def get_open_link(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> str: ...

    @abstractmethod
    def update_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        name: str | None = None,
        parent_id: str | None = None,
    ) -> FileItemDTO: ...

    @abstractmethod
    def delete_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        permanent: bool = False,
    ) -> None: ...

    @abstractmethod
    def copy_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
        parent_id: str,
        name: str | None = None,
    ) -> FileItemDTO: ...

    @abstractmethod
    def restore_item(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> FileItemDTO: ...

    @abstractmethod
    def get_breadcrumb(
        self,
        *,
        credentials: dict[str, Any],
        item_id: str,
    ) -> list[FileItemDTO]: ...

    @abstractmethod
    def get_quota(
        self,
        *,
        credentials: dict[str, Any],
    ) -> QuotaSummaryDTO: ...
