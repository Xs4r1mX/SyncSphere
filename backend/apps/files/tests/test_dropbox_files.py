from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from django.test import TestCase

import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata, FolderMetadata, ListFolderResult, LookupError

from apps.common.exceptions import (
    FileNotFoundException,
    InvalidFileOperationException,
    ProviderAuthException,
)
from apps.files.providers.dropbox import DropboxFileAdapter, ROOT_ITEM_ID


def _folder_metadata(*, item_id="folder-id", name="Docs", path="/Docs"):
    return FolderMetadata(
        name=name,
        id=f"id:{item_id}",
        path_display=path,
        path_lower=path.lower(),
    )


def _file_metadata(*, item_id="file-id", name="notes.txt", path="/notes.txt", size=12):
    return FileMetadata(
        name=name,
        id=f"id:{item_id}",
        client_modified=datetime(2026, 1, 1, tzinfo=timezone.utc),
        server_modified=datetime(2026, 1, 2, tzinfo=timezone.utc),
        path_display=path,
        path_lower=path.lower(),
        size=size,
    )


class DropboxFileAdapterTests(TestCase):
    def setUp(self):
        self.adapter = DropboxFileAdapter()

    def test_to_api_ref_maps_root_and_ids(self):
        self.assertEqual(self.adapter._to_api_ref(ROOT_ITEM_ID), "")
        self.assertEqual(self.adapter._to_api_ref("abc123"), "id:abc123")
        self.assertEqual(self.adapter._to_api_ref("id:abc123"), "id:abc123")

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_list_items_at_root_uses_empty_path(self, mock_build_client):
        client = MagicMock()
        mock_build_client.return_value = client
        client.files_list_folder.return_value = ListFolderResult(
            entries=[_file_metadata()],
            cursor="cursor-1",
            has_more=False,
        )

        result = self.adapter.list_items(
            credentials={"access_token": "token"},
            parent_id=ROOT_ITEM_ID,
        )

        client.files_list_folder.assert_called_once()
        call_args = client.files_list_folder.call_args
        self.assertEqual(call_args.args[0], "")
        self.assertEqual(call_args.kwargs.get("limit"), 50)
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].provider_item_id, "file-id")

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_get_item_root_returns_virtual_folder(self, mock_build_client):
        item = self.adapter.get_item(
            credentials={"access_token": "token"},
            item_id=ROOT_ITEM_ID,
        )

        self.assertTrue(item.is_folder)
        self.assertEqual(item.provider_item_id, ROOT_ITEM_ID)
        mock_build_client.assert_not_called()

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_upload_file_builds_path_under_parent(self, mock_build_client):
        client = MagicMock()
        mock_build_client.return_value = client
        client.files_get_metadata.return_value = _folder_metadata(
            item_id="parent-id",
            path="/Parent",
        )
        client.files_upload.return_value = _file_metadata(
            item_id="new-file",
            name="upload.txt",
            path="/Parent/upload.txt",
        )

        uploaded = self.adapter.upload_file(
            credentials={"access_token": "token"},
            name="upload.txt",
            parent_id="parent-id",
            content=b"hello",
            content_type="text/plain",
        )

        client.files_upload.assert_called_once()
        upload_args = client.files_upload.call_args.args
        self.assertEqual(upload_args[0], b"hello")
        self.assertEqual(upload_args[1], "/Parent/upload.txt")
        self.assertEqual(uploaded.provider_item_id, "new-file")

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_download_file_rejects_folders(self, mock_build_client):
        client = MagicMock()
        mock_build_client.return_value = client
        client.files_get_metadata.return_value = _folder_metadata()

        with self.assertRaises(InvalidFileOperationException):
            self.adapter.download_file(
                credentials={"access_token": "token"},
                item_id="folder-id",
            )

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_download_file_returns_bytes(self, mock_build_client):
        client = MagicMock()
        mock_build_client.return_value = client
        client.files_get_metadata.return_value = _file_metadata()
        response = MagicMock()
        response.content = b"payload"
        client.files_download.return_value = (_file_metadata(), response)

        downloaded = self.adapter.download_file(
            credentials={"access_token": "token"},
            item_id="file-id",
        )

        self.assertEqual(downloaded.content, b"payload")
        self.assertEqual(downloaded.name, "notes.txt")

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_not_found_maps_to_file_not_found_exception(self, mock_build_client):
        client = MagicMock()
        mock_build_client.return_value = client
        client.files_get_metadata.side_effect = ApiError(
            "request-id",
            LookupError("not_found", None),
            None,
            None,
        )

        with self.assertRaises(FileNotFoundException):
            self.adapter.get_item(
                credentials={"access_token": "token"},
                item_id="missing-id",
            )

    @patch.object(DropboxFileAdapter, "_build_client")
    def test_auth_error_maps_to_provider_auth_exception(self, mock_build_client):
        client = MagicMock()
        mock_build_client.return_value = client
        client.files_get_metadata.side_effect = dropbox.exceptions.AuthError(
            "request-id",
            MagicMock(),
        )

        with self.assertRaises(ProviderAuthException):
            self.adapter.get_item(
                credentials={"access_token": "token"},
                item_id="file-id",
            )
