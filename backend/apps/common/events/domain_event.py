from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DomainEvent:
    """
    Immutable domain event published by services for observers.

    metadata must be safe (no tokens, file content, or credentials).
    """

    action: str
    user_id: int
    resource_type: str
    resource_id: str = ""
    resource_name: str = ""
    connection_id: int | None = None
    provider: str = ""
    status: str = "success"
    metadata: dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        occurred_at = payload.get("occurred_at")
        if isinstance(occurred_at, datetime):
            payload["occurred_at"] = occurred_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DomainEvent":
        data = dict(payload)
        occurred_at = data.get("occurred_at")
        if isinstance(occurred_at, str):
            data["occurred_at"] = datetime.fromisoformat(occurred_at)
        elif occurred_at is None:
            data.pop("occurred_at", None)
        return cls(**data)
