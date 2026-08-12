from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.cloud.services import ConnectionService
from apps.common.constants import ConnectionStatus, ProviderType
from apps.files.dto import FileDownloadDTO, FileItemDTO, FileListResultDTO, QuotaSummaryDTO
from apps.transfers.constants import (
    TransferConflictPolicy,
    TransferItemStatus,
    TransferJobStatus,
    TransferOperation,
)
from apps.transfers.models import TransferJob
from apps.transfers.services.transfer_executor import TransferExecutor
from apps.transfers.services.transfer_service import TransferService

User = get_user_model()


def _file_item(item_id, name, *, size=10, is_folder=False, parent_id="root"):
    return FileItemDTO(
        provider_item_id=item_id,
        name=name,
        mime_type="application/vnd.google-apps.folder" if is_folder else "text/plain",
        is_folder=is_folder,
        parent_id=parent_id,
        size=None if is_folder else size,
    )


class TransferExecutorSafetyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="xfer@example.com",
            first_name="X",
            last_name="Fer",
            password="SecurePass123!",
        )
        self.source = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Source",
            provider_account_id="src-1",
            credentials={
                "access_token": "a",
                "refresh_token": "r",
                "token_expiry": "2099-01-01T00:00:00+00:00",
            },
            status=ConnectionStatus.ACTIVE,
        )
        self.dest = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Dest",
            provider_account_id="dst-1",
            credentials={
                "access_token": "a2",
                "refresh_token": "r2",
                "token_expiry": "2099-01-01T00:00:00+00:00",
            },
            status=ConnectionStatus.ACTIVE,
        )

    def _create_job(self, operation=TransferOperation.MOVE):
        return TransferJob.objects.create(
            user=self.user,
            source_connection=self.source,
            dest_connection=self.dest,
            operation=operation,
            conflict_policy=TransferConflictPolicy.REJECT,
            source_item_id="file-1",
            dest_parent_id="root",
            status=TransferJobStatus.PENDING,
        )

    @patch("apps.transfers.services.transfer_executor.FileService")
    @patch("apps.transfers.services.transfer_planner.FileService")
    @patch("apps.transfers.services.name_resolver.FileService")
    def test_move_deletes_source_only_after_upload_success(
        self,
        mock_name_fs,
        mock_plan_fs,
        mock_exec_fs,
    ):
        mock_plan_fs.get_item.return_value = _file_item("file-1", "notes.txt", size=5)
        mock_name_fs.list_items.return_value = FileListResultDTO(items=[], next_page_token=None)

        mock_exec_fs.get_quota.return_value = QuotaSummaryDTO(1000, 0, 1000)
        mock_exec_fs.download_file.return_value = FileDownloadDTO(
            content=b"hello",
            name="notes.txt",
            content_type="text/plain",
            size=5,
        )
        uploaded = _file_item("dest-1", "notes.txt", size=5)
        mock_exec_fs.upload_file.return_value = uploaded
        mock_exec_fs.get_item.return_value = uploaded

        call_order = []

        def download(*args, **kwargs):
            call_order.append("download")
            return mock_exec_fs.download_file.return_value

        def upload(*args, **kwargs):
            call_order.append("upload")
            return uploaded

        def verify(*args, **kwargs):
            call_order.append("verify")
            return uploaded

        def delete(*args, **kwargs):
            call_order.append("delete")

        mock_exec_fs.download_file.side_effect = download
        mock_exec_fs.upload_file.side_effect = upload
        mock_exec_fs.get_item.side_effect = verify
        mock_exec_fs.delete_item.side_effect = delete

        job = self._create_job(TransferOperation.MOVE)
        result = TransferExecutor.run(job_uuid=job.uuid)

        self.assertEqual(result.status, TransferJobStatus.SUCCESS)
        self.assertEqual(call_order, ["download", "upload", "verify", "delete"])
        mock_exec_fs.delete_item.assert_called_once()

    @patch("apps.transfers.services.transfer_executor.FileService")
    @patch("apps.transfers.services.transfer_planner.FileService")
    @patch("apps.transfers.services.name_resolver.FileService")
    def test_upload_failure_never_deletes_source(
        self,
        mock_name_fs,
        mock_plan_fs,
        mock_exec_fs,
    ):
        mock_plan_fs.get_item.return_value = _file_item("file-1", "notes.txt", size=5)
        mock_name_fs.list_items.return_value = FileListResultDTO(items=[], next_page_token=None)
        mock_exec_fs.get_quota.return_value = QuotaSummaryDTO(1000, 0, 1000)
        mock_exec_fs.download_file.return_value = FileDownloadDTO(
            content=b"hello",
            name="notes.txt",
            content_type="text/plain",
            size=5,
        )
        mock_exec_fs.upload_file.side_effect = RuntimeError("upload boom")

        job = self._create_job(TransferOperation.MOVE)
        result = TransferExecutor.run(job_uuid=job.uuid)

        self.assertEqual(result.status, TransferJobStatus.FAILED)
        mock_exec_fs.delete_item.assert_not_called()
        item = result.items.first()
        self.assertEqual(item.status, TransferItemStatus.FAILED)

    @patch("apps.transfers.services.transfer_executor.FileService")
    @patch("apps.transfers.services.transfer_planner.FileService")
    @patch("apps.transfers.services.name_resolver.FileService")
    def test_insufficient_space_blocks_before_transfer(
        self,
        mock_name_fs,
        mock_plan_fs,
        mock_exec_fs,
    ):
        mock_plan_fs.get_item.return_value = _file_item("file-1", "big.txt", size=500)
        mock_name_fs.list_items.return_value = FileListResultDTO(items=[], next_page_token=None)
        mock_exec_fs.get_quota.return_value = QuotaSummaryDTO(1000, 900, 100)

        job = self._create_job(TransferOperation.COPY)
        result = TransferExecutor.run(job_uuid=job.uuid)

        self.assertEqual(result.status, TransferJobStatus.FAILED)
        self.assertIn("InsufficientStorage", result.error_code)
        mock_exec_fs.download_file.assert_not_called()
        mock_exec_fs.upload_file.assert_not_called()

    @patch("apps.transfers.services.transfer_executor.FileService")
    @patch("apps.transfers.services.transfer_planner.FileService")
    @patch("apps.transfers.services.name_resolver.FileService")
    def test_copy_all_creates_folder_then_files(
        self,
        mock_name_fs,
        mock_plan_fs,
        mock_exec_fs,
    ):
        folder = _file_item("folder-1", "Docs", is_folder=True)
        child = _file_item("file-2", "a.txt", size=3, parent_id="folder-1")

        mock_plan_fs.get_item.return_value = folder
        mock_plan_fs.list_items.return_value = FileListResultDTO(
            items=[child],
            next_page_token=None,
        )
        mock_name_fs.list_items.return_value = FileListResultDTO(items=[], next_page_token=None)

        mock_exec_fs.get_quota.return_value = QuotaSummaryDTO(1000, 0, 1000)
        created_folder = _file_item("dest-folder", "Docs", is_folder=True)
        uploaded = _file_item("dest-file", "a.txt", size=3)

        def get_item_side_effect(*, user, connection_uuid, item_id):
            if item_id == "dest-folder":
                return created_folder
            if item_id == "dest-file":
                return uploaded
            return folder

        mock_exec_fs.create_folder.return_value = created_folder
        mock_exec_fs.get_item.side_effect = get_item_side_effect
        mock_exec_fs.download_file.return_value = FileDownloadDTO(
            content=b"abc",
            name="a.txt",
            content_type="text/plain",
            size=3,
        )
        mock_exec_fs.upload_file.return_value = uploaded

        job = self._create_job(TransferOperation.COPY_ALL)
        job.source_item_id = "folder-1"
        job.save(update_fields=["source_item_id"])

        result = TransferExecutor.run(job_uuid=job.uuid)
        self.assertEqual(result.status, TransferJobStatus.SUCCESS)
        self.assertEqual(result.items_total, 2)
        mock_exec_fs.create_folder.assert_called_once()
        mock_exec_fs.upload_file.assert_called_once()
        mock_exec_fs.delete_item.assert_not_called()


class TransferServiceAPIFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="api-xfer@example.com",
            first_name="A",
            last_name="P",
            password="SecurePass123!",
        )
        self.source = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Source",
            provider_account_id="src-api",
            credentials={"access_token": "a", "refresh_token": "r"},
            status=ConnectionStatus.ACTIVE,
        )
        self.dest = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Dest",
            provider_account_id="dst-api",
            credentials={"access_token": "a2", "refresh_token": "r2"},
            status=ConnectionStatus.ACTIVE,
        )

    @patch("apps.transfers.tasks.run_transfer.execute_transfer.apply_async")
    def test_create_enqueues_task(self, mock_apply_async):
        mock_apply_async.return_value = MagicMock(id="celery-1")

        job = TransferService.create_transfer(
            user=self.user,
            operation=TransferOperation.COPY,
            source_connection_uuid=self.source.uuid,
            dest_connection_uuid=self.dest.uuid,
            source_item_id="file-9",
            request_id="req-1",
        )

        self.assertEqual(job.status, TransferJobStatus.PENDING)
        self.assertEqual(job.celery_task_id, "celery-1")
        mock_apply_async.assert_called_once()

    def test_cancel_pending_job(self):
        job = TransferJob.objects.create(
            user=self.user,
            source_connection=self.source,
            dest_connection=self.dest,
            operation=TransferOperation.COPY,
            source_item_id="file-1",
            status=TransferJobStatus.PENDING,
        )
        cancelled = TransferService.cancel_transfer(
            user=self.user,
            job_uuid=job.uuid,
        )
        self.assertEqual(cancelled.status, TransferJobStatus.CANCELLED)
        self.assertTrue(cancelled.cancel_requested)
