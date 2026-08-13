from apps.common.exceptions import TransferConflictException
from apps.files.services import FileService
from apps.transfers.constants import TransferConflictPolicy


class DestinationNameResolver:
    """
    Resolves conflict-free destination names for one transfer job.

    Caches destination child names by parent id so each folder is listed at
    most once. Newly chosen names are tracked so rename stays correct
    without re-hitting the provider.
    """

    def __init__(self, *, user, connection_uuid, conflict_policy: str) -> None:
        self._user = user
        self._connection_uuid = connection_uuid
        self._conflict_policy = conflict_policy
        self._names_by_parent: dict[str, set[str]] = {}

    def resolve(self, *, parent_id: str, desired_name: str) -> str:
        """
        Return a destination name that does not conflict, or raise.

        rename policy appends ' (n)' before the extension / at end of folder name.
        """
        existing = self._child_names(parent_id=parent_id)
        if desired_name not in existing:
            self.remember(parent_id=parent_id, name=desired_name)
            return desired_name

        if self._conflict_policy == TransferConflictPolicy.REJECT:
            raise TransferConflictException(
                f"'{desired_name}' already exists at the destination."
            )

        resolved = self._next_available_name(desired_name, existing)
        self.remember(parent_id=parent_id, name=resolved)
        return resolved

    def remember(self, *, parent_id: str, name: str) -> None:
        key = str(parent_id)
        if key not in self._names_by_parent:
            self._names_by_parent[key] = set()
        if name:
            self._names_by_parent[key].add(name)

    def seed_empty(self, *, parent_id: str) -> None:
        """Mark a newly created folder as listed with no children."""
        key = str(parent_id)
        if key not in self._names_by_parent:
            self._names_by_parent[key] = set()

    def _child_names(self, *, parent_id: str) -> set[str]:
        key = str(parent_id)
        if key not in self._names_by_parent:
            self._names_by_parent[key] = self._list_child_names(parent_id=parent_id)
        return self._names_by_parent[key]

    def _list_child_names(self, *, parent_id: str) -> set[str]:
        names: set[str] = set()
        page_token = None
        while True:
            result = FileService.list_items(
                user=self._user,
                connection_uuid=self._connection_uuid,
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

    @staticmethod
    def _next_available_name(desired_name: str, existing: set[str]) -> str:
        stem, ext = DestinationNameResolver._split_name(desired_name)
        counter = 1
        while True:
            candidate = f"{stem} ({counter}){ext}"
            if candidate not in existing:
                return candidate
            counter += 1

    @staticmethod
    def _split_name(name: str) -> tuple[str, str]:
        if "." in name and not name.startswith("."):
            stem, ext = name.rsplit(".", 1)
            return stem, f".{ext}"
        return name, ""
