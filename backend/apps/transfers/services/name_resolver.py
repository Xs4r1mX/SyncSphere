from apps.common.exceptions import TransferConflictException
from apps.files.services import FileService
from apps.transfers.constants import TransferConflictPolicy


def resolve_destination_name(
    *,
    user,
    connection_uuid,
    parent_id: str,
    desired_name: str,
    conflict_policy: str,
) -> str:
    """
    Return a destination name that does not conflict, or raise.

    rename policy appends ' (n)' before the extension / at end of folder name.
    """
    existing = _list_child_names(
        user=user,
        connection_uuid=connection_uuid,
        parent_id=parent_id,
    )
    if desired_name not in existing:
        return desired_name

    if conflict_policy == TransferConflictPolicy.REJECT:
        raise TransferConflictException(
            f"'{desired_name}' already exists at the destination."
        )

    return _next_available_name(desired_name, existing)


def _list_child_names(*, user, connection_uuid, parent_id: str) -> set[str]:
    names: set[str] = set()
    page_token = None
    while True:
        result = FileService.list_items(
            user=user,
            connection_uuid=connection_uuid,
            parent_id=parent_id,
            page_token=page_token,
            page_size=100,
            trashed=False,
        )
        for item in result.items:
            names.add(item.name)
        if not result.next_page_token:
            break
        page_token = result.next_page_token
    return names


def _next_available_name(desired_name: str, existing: set[str]) -> str:
    stem, ext = _split_name(desired_name)
    counter = 1
    while True:
        candidate = f"{stem} ({counter}){ext}"
        if candidate not in existing:
            return candidate
        counter += 1


def _split_name(name: str) -> tuple[str, str]:
    if "." in name and not name.startswith("."):
        stem, ext = name.rsplit(".", 1)
        return stem, f".{ext}"
    return name, ""
