import logging
from dataclasses import dataclass

from django.db import transaction

from apps.common.exceptions import (
    TransferOperationMismatchException,
    TransferTooLargeException,
)
from apps.files.dto import FileItemDTO
from apps.files.services import FileService
from apps.transfers.constants import (
    TransferItemKind,
    TransferItemStatus,
    TransferJobStatus,
    TransferOperation,
)
from apps.transfers.models import TransferItem, TransferJob
from apps.transfers.services.name_resolver import resolve_destination_name

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlannedNode:
    kind: str
    source_item_id: str
    source_name: str
    source_path: str
    size_bytes: int
    mime_type: str
    parent_source_id: str | None


class TransferPlanner:
    """Builds ordered TransferItem rows and validates size before any write."""

    @staticmethod
    @transaction.atomic
    def build_plan(*, job: TransferJob) -> TransferJob:
        job.status = TransferJobStatus.PLANNING
        job.save(update_fields=["status", "updated_at"])

        source_uuid = job.source_connection.uuid
        user = job.user

        source_item = FileService.get_item(
            user=user,
            connection_uuid=source_uuid,
            item_id=job.source_item_id,
        )
        TransferPlanner._validate_operation_match(job.operation, source_item)

        job.source_item_name = source_item.name
        job.source_is_folder = source_item.is_folder

        nodes = TransferPlanner._collect_nodes(
            user=user,
            connection_uuid=source_uuid,
            root=source_item,
            operation=job.operation,
        )

        total_bytes = sum(node.size_bytes for node in nodes if node.kind == TransferItemKind.FILE)
        TransferPlanner._enforce_size_limit(total_bytes)

        root_dest_name = resolve_destination_name(
            user=user,
            connection_uuid=job.dest_connection.uuid,
            parent_id=job.dest_parent_id,
            desired_name=source_item.name,
            conflict_policy=job.conflict_policy,
        )

        TransferItem.objects.filter(job=job).delete()
        TransferPlanner._persist_items(
            job=job,
            nodes=nodes,
            root_source_id=source_item.provider_item_id,
            root_dest_parent_id=job.dest_parent_id,
            root_dest_name=root_dest_name,
        )

        job.total_bytes = total_bytes
        job.items_total = job.items.count()
        job.items_completed = 0
        job.items_failed = 0
        job.save(
            update_fields=[
                "source_item_name",
                "source_is_folder",
                "total_bytes",
                "items_total",
                "items_completed",
                "items_failed",
                "updated_at",
            ]
        )

        logger.info(
            "Transfer plan built",
            extra={
                "job_uuid": str(job.uuid),
                "items_total": job.items_total,
                "total_bytes": job.total_bytes,
                "operation": job.operation,
            },
        )
        return job

    @staticmethod
    def _validate_operation_match(operation: str, source_item: FileItemDTO) -> None:
        if operation in (TransferOperation.COPY, TransferOperation.MOVE):
            if source_item.is_folder:
                raise TransferOperationMismatchException(
                    "copy/move require a file source. Use copy_all/move_all for folders."
                )
        elif operation in (TransferOperation.COPY_ALL, TransferOperation.MOVE_ALL):
            if not source_item.is_folder:
                raise TransferOperationMismatchException(
                    "copy_all/move_all require a folder source."
                )

    @staticmethod
    def _enforce_size_limit(total_bytes: int) -> None:
        from django.conf import settings

        max_bytes = settings.MAX_TRANSFER_SIZE_BYTES
        if total_bytes > max_bytes:
            raise TransferTooLargeException(
                f"Transfer size {total_bytes} exceeds limit {max_bytes} bytes."
            )

    @staticmethod
    def _collect_nodes(
        *,
        user,
        connection_uuid,
        root: FileItemDTO,
        operation: str,
    ) -> list[PlannedNode]:
        if operation in (TransferOperation.COPY, TransferOperation.MOVE):
            size = root.size or 0
            return [
                PlannedNode(
                    kind=TransferItemKind.FILE,
                    source_item_id=root.provider_item_id,
                    source_name=root.name,
                    source_path=root.name,
                    size_bytes=size,
                    mime_type=root.mime_type,
                    parent_source_id=None,
                )
            ]

        nodes: list[PlannedNode] = [
            PlannedNode(
                kind=TransferItemKind.FOLDER,
                source_item_id=root.provider_item_id,
                source_name=root.name,
                source_path=root.name,
                size_bytes=0,
                mime_type=root.mime_type,
                parent_source_id=None,
            )
        ]
        TransferPlanner._walk_folder(
            user=user,
            connection_uuid=connection_uuid,
            folder=root,
            path_prefix=root.name,
            nodes=nodes,
        )
        return nodes

    @staticmethod
    def _walk_folder(
        *,
        user,
        connection_uuid,
        folder: FileItemDTO,
        path_prefix: str,
        nodes: list[PlannedNode],
    ) -> None:
        page_token = None
        while True:
            result = FileService.list_items(
                user=user,
                connection_uuid=connection_uuid,
                parent_id=folder.provider_item_id,
                page_token=page_token,
                page_size=100,
                trashed=False,
            )
            for child in result.items:
                child_path = f"{path_prefix}/{child.name}"
                if child.is_folder:
                    nodes.append(
                        PlannedNode(
                            kind=TransferItemKind.FOLDER,
                            source_item_id=child.provider_item_id,
                            source_name=child.name,
                            source_path=child_path,
                            size_bytes=0,
                            mime_type=child.mime_type,
                            parent_source_id=folder.provider_item_id,
                        )
                    )
                    TransferPlanner._walk_folder(
                        user=user,
                        connection_uuid=connection_uuid,
                        folder=child,
                        path_prefix=child_path,
                        nodes=nodes,
                    )
                else:
                    nodes.append(
                        PlannedNode(
                            kind=TransferItemKind.FILE,
                            source_item_id=child.provider_item_id,
                            source_name=child.name,
                            source_path=child_path,
                            size_bytes=child.size or 0,
                            mime_type=child.mime_type,
                            parent_source_id=folder.provider_item_id,
                        )
                    )
            if not result.next_page_token:
                break
            page_token = result.next_page_token

    @staticmethod
    def _persist_items(
        *,
        job: TransferJob,
        nodes: list[PlannedNode],
        root_source_id: str,
        root_dest_parent_id: str,
        root_dest_name: str,
    ) -> None:
        # dest_parent_id stores:
        # - root item: job.dest_parent_id
        # - nested: parent source folder id (mapped to dest id during execute)
        bulk: list[TransferItem] = []
        for index, node in enumerate(nodes):
            if node.parent_source_id is None:
                dest_parent_ref = root_dest_parent_id
                dest_name = root_dest_name
            else:
                dest_parent_ref = node.parent_source_id
                dest_name = node.source_name

            bulk.append(
                TransferItem(
                    job=job,
                    sequence=index,
                    kind=node.kind,
                    source_item_id=node.source_item_id,
                    source_path=node.source_path,
                    source_name=node.source_name,
                    dest_parent_id=dest_parent_ref,
                    dest_name=dest_name,
                    size_bytes=node.size_bytes,
                    mime_type=node.mime_type,
                    status=TransferItemStatus.PENDING,
                )
            )

        TransferItem.objects.bulk_create(bulk)
