from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FileItemDTO:
    provider_item_id: str
    name: str
    mime_type: str
    is_folder: bool
    parent_id: str | None = None
    size: int | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    trashed: bool = False
    web_view_link: str | None = None
    can_open: bool = False
    can_download: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_item_id": self.provider_item_id,
            "name": self.name,
            "mime_type": self.mime_type,
            "is_folder": self.is_folder,
            "parent_id": self.parent_id,
            "size": self.size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "trashed": self.trashed,
            "web_view_link": self.web_view_link,
            "can_open": self.can_open,
            "can_download": self.can_download,
        }


@dataclass(frozen=True)
class FileListResultDTO:
    items: list[FileItemDTO] = field(default_factory=list)
    next_page_token: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [item.to_dict() for item in self.items],
            "next_page_token": self.next_page_token,
        }


@dataclass(frozen=True)
class FileDownloadDTO:
    content: bytes
    name: str
    content_type: str
    size: int


@dataclass(frozen=True)
class QuotaSummaryDTO:
    quota_total_bytes: int | None
    quota_used_bytes: int | None
    quota_available_bytes: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "quota_total_bytes": self.quota_total_bytes,
            "quota_used_bytes": self.quota_used_bytes,
            "quota_available_bytes": self.quota_available_bytes,
        }
