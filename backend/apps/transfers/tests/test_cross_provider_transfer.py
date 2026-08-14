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


class CrossProviderTransferTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="cross@example.com",
            first_name="Cross",
            last_name="Provider",
            password="SecurePass123!",
        )
        self.google_source = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Google Source",
            provider_account_id="gdrive-src",
            credentials={
                "access_token": "g-access",
                "refresh_token": "g-refresh",
                "token_expiry": "2099-01-01T00:00:00+00:00",
            },
            status=ConnectionStatus.ACTIVE,
        )
        self.dropbox_dest = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.DROPBOX,
            display_name="Dropbox Dest",
            provider_account_id="dbx-dst",
            credentials={
                "access_token": "d-access",
                "refresh_token": "d-refresh",
                "token_expiry": "2099-01-01T00:00:00+00:00",
            },
            status=ConnectionStatus.ACTIVE,
        )

    @patch("apps.transfers.services.transfer_executor.FileService")
    @patch("apps.transfers.services.transfer_planner.FileService")
    @patch("apps.transfers.services.name_resolver.FileService")
    def test_google_drive_to_dropbox_copy_succeeds(
        self,
        mock_name_fs,
        mock_plan_fs,
        mock_exec_fs,
    ):
        mock_plan_fs.get_item.return_value = _file_item("gdrive-file", "report.pdf", size=8)
        mock_name_fs.list_items.return_value = FileListResultDTO(items=[], next_page_token=None)

        mock_exec_fs.get_quota.return_value = QuotaSummaryDTO(10000, 0, 10000)
        mock_exec_fs.download_file.return_value = FileDownloadDTO(
            content=b"pdf-data",
            name="report.pdf",
            content_type="application/pdf",
            size=8,
        )
        uploaded = _file_item("dbx-file", "report.pdf", size=8)
        mock_exec_fs.upload_file.return_value = uploaded
        mock_exec_fs.get_item.return_value = uploaded

        job = TransferJob.objects.create(
            user=self.user,
            source_connection=self.google_source,
            dest_connection=self.dropbox_dest,
            operation=TransferOperation.COPY,
            conflict_policy=TransferConflictPolicy.REJECT,
            source_item_id="gdrive-file",
            dest_parent_id="root",
            status=TransferJobStatus.PENDING,
        )

        result = TransferExecutor.run(job_uuid=job.uuid)

        self.assertEqual(result.status, TransferJobStatus.SUCCESS)
        mock_exec_fs.download_file.assert_called_once()
        mock_exec_fs.upload_file.assert_called_once()
        mock_exec_fs.delete_item.assert_not_called()
        item = result.items.first()
        self.assertEqual(item.status, TransferItemStatus.SUCCESS)
        self.assertEqual(item.dest_item_id, "dbx-file")

    @patch("apps.transfers.services.transfer_executor.FileService")
    @patch("apps.transfers.services.transfer_planner.FileService")
    @patch("apps.transfers.services.name_resolver.FileService")
    def test_google_drive_to_dropbox_move_deletes_after_verify(
        self,
        mock_name_fs,
        mock_plan_fs,
        mock_exec_fs,
    ):
        mock_plan_fs.get_item.return_value = _file_item("gdrive-file", "notes.txt", size=5)
        mock_name_fs.list_items.return_value = FileListResultDTO(items=[], next_page_token=None)

        mock_exec_fs.get_quota.return_value = QuotaSummaryDTO(10000, 0, 10000)
        mock_exec_fs.download_file.return_value = FileDownloadDTO(
            content=b"hello",
            name="notes.txt",
            content_type="text/plain",
            size=5,
        )
        uploaded = _file_item("dbx-file", "notes.txt", size=5)
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

        job = TransferJob.objects.create(
            user=self.user,
            source_connection=self.google_source,
            dest_connection=self.dropbox_dest,
            operation=TransferOperation.MOVE,
            conflict_policy=TransferConflictPolicy.REJECT,
            source_item_id="gdrive-file",
            dest_parent_id="root",
            status=TransferJobStatus.PENDING,
        )

        result = TransferExecutor.run(job_uuid=job.uuid)

        self.assertEqual(result.status, TransferJobStatus.SUCCESS)
        self.assertEqual(call_order, ["download", "upload", "verify", "delete"])
        mock_exec_fs.delete_item.assert_called_once()
