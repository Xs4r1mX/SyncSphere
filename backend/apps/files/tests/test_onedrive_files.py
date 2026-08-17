import json
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.common.exceptions import (
    FileNotFoundException,
    InvalidFileOperationException,
    ProviderAuthException,
)
from apps.files.providers.onedrive import OneDriveFileAdapter, ROOT_ITEM_ID


def _file_payload(
    *,
    item_id="file-id",
    name="notes.txt",
    parent_id="parent-id",
    web_url="https://onedrive.live.com/view.aspx?resid=file-id",
):
    return {
        "id": item_id,
        "name": name,
        "size": 12,
        "file": {"mimeType": "text/plain"},
        "createdDateTime": "2026-01-01T00:00:00Z",
        "lastModifiedDateTime": "2026-01-02T00:00:00Z",
        "webUrl": web_url,
        "parentReference": {"id": parent_id},
    }


class OneDriveFileAdapterTests(TestCase):
    def setUp(self):
        self.adapter = OneDriveFileAdapter()

    def test_children_path_maps_root(self):
        self.assertEqual(
            self.adapter._children_path(ROOT_ITEM_ID),
            "/me/drive/root/children",
        )
        self.assertEqual(
            self.adapter._children_path("folder-id"),
            "/me/drive/items/folder-id/children",
        )

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_list_items_at_root(self, mock_graph_request):
        mock_graph_request.return_value = {
            "value": [_file_payload()],
        }

        result = self.adapter.list_items(
            credentials={"access_token": "token"},
            parent_id=ROOT_ITEM_ID,
        )

        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        self.assertIn("/me/drive/root/children", call_args.args[1])
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].provider_item_id, "file-id")

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_get_item_root_returns_virtual_folder(self, mock_graph_request):
        item = self.adapter.get_item(
            credentials={"access_token": "token"},
            item_id=ROOT_ITEM_ID,
        )

        self.assertTrue(item.is_folder)
        self.assertEqual(item.provider_item_id, ROOT_ITEM_ID)
        mock_graph_request.assert_not_called()

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_get_open_link_returns_web_url(self, mock_graph_request):
        mock_graph_request.return_value = _file_payload()

        url = self.adapter.get_open_link(
            credentials={"access_token": "token"},
            item_id="file-id",
        )

        self.assertEqual(
            url,
            "https://onedrive.live.com/view.aspx?resid=file-id",
        )

    @patch.object(OneDriveFileAdapter, "_fetch_preauthenticated_url")
    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_download_file_returns_content(
        self, mock_graph_request, mock_fetch_url
    ):
        metadata = _file_payload()
        mock_graph_request.side_effect = [
            metadata,
            {"@microsoft.graph.downloadUrl": "https://download.example/content"},
        ]
        mock_fetch_url.return_value = b"hello world"

        download = self.adapter.download_file(
            credentials={"access_token": "token"},
            item_id="file-id",
        )

        self.assertEqual(download.content, b"hello world")
        self.assertEqual(download.name, "notes.txt")
        self.assertEqual(download.content_type, "text/plain")
        mock_fetch_url.assert_called_once_with("https://download.example/content")

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_download_file_rejects_folders(self, mock_graph_request):
        mock_graph_request.return_value = {
            "id": "folder-id",
            "name": "Docs",
            "folder": {},
            "parentReference": {"id": ROOT_ITEM_ID},
        }

        with self.assertRaises(InvalidFileOperationException):
            self.adapter.download_file(
                credentials={"access_token": "token"},
                item_id="folder-id",
            )

    @patch("urllib.request.urlopen")
    def test_list_items_maps_404_to_not_found(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://graph.microsoft.com/v1.0/me/drive/root/children",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )

        with self.assertRaises(FileNotFoundException):
            self.adapter.list_items(
                credentials={"access_token": "token"},
                parent_id=ROOT_ITEM_ID,
            )

    def test_missing_access_token_raises_auth_error(self):
        with self.assertRaises(ProviderAuthException):
            self.adapter.list_items(credentials={}, parent_id=ROOT_ITEM_ID)

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_list_trashed_items_raises(self, mock_graph_request):
        with self.assertRaises(InvalidFileOperationException):
            self.adapter.list_items(
                credentials={"access_token": "token"},
                parent_id=ROOT_ITEM_ID,
                trashed=True,
            )

        mock_graph_request.assert_not_called()

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_copy_item_resolves_root_parent(self, mock_graph_request):
        mock_graph_request.side_effect = [
            {"id": "source-id"},
            {"id": "my-drive-id"},
            {"id": "drive-root-id"},
            _file_payload(item_id="copied-id", parent_id="drive-root-id"),
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            copy_response = MagicMock()
            copy_response.headers = {
                "Location": (
                    "https://my.microsoftpersonalcontent.com/personal/user"
                    "/_api/v2.0/monitor/copy?tempauth=token"
                )
            }
            copy_response.__enter__.return_value = copy_response

            poll_response = MagicMock()
            poll_response.read.return_value = json.dumps(
                {"status": "completed", "resourceId": "copied-id"}
            ).encode("utf-8")
            poll_response.__enter__.return_value = poll_response

            mock_urlopen.side_effect = [copy_response, poll_response]

            copied = self.adapter.copy_item(
                credentials={"access_token": "token"},
                item_id="source-id",
                parent_id=ROOT_ITEM_ID,
                name="Copy.txt",
            )

        self.assertEqual(copied.provider_item_id, "copied-id")
        copy_request = mock_urlopen.call_args_list[0].args[0]
        body = json.loads(copy_request.data.decode("utf-8"))
        self.assertEqual(body["parentReference"]["driveId"], "my-drive-id")
        self.assertEqual(body["parentReference"]["id"], "drive-root-id")
        self.assertNotIn("@microsoft.graph.conflictBehavior", body)
        self.assertIn("/me/drive/items/source-id/copy", copy_request.full_url)

        poll_request = mock_urlopen.call_args_list[1].args[0]
        self.assertNotIn("Authorization", poll_request.headers)

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_copy_item_uses_remote_drive_for_shared_items(self, mock_graph_request):
        mock_graph_request.side_effect = [
            {
                "id": "BBA0AD4DACE00FE1!se8af4fc0fb5a4fef8befbb62f4200a39",
                "remoteItem": {
                    "id": "remote-item-id",
                    "parentReference": {"driveId": "remote-drive-id"},
                },
            },
            {"id": "my-drive-id"},
            {"id": "drive-root-id"},
            _file_payload(item_id="copied-id", parent_id="drive-root-id"),
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            copy_response = MagicMock()
            copy_response.headers = {
                "Location": (
                    "https://my.microsoftpersonalcontent.com/personal/user"
                    "/_api/v2.0/monitor/copy?tempauth=token"
                )
            }
            copy_response.__enter__.return_value = copy_response

            poll_response = MagicMock()
            poll_response.read.return_value = json.dumps(
                {"status": "completed", "resourceId": "copied-id"}
            ).encode("utf-8")
            poll_response.__enter__.return_value = poll_response

            mock_urlopen.side_effect = [copy_response, poll_response]

            copied = self.adapter.copy_item(
                credentials={"access_token": "token"},
                item_id="BBA0AD4DACE00FE1!se8af4fc0fb5a4fef8befbb62f4200a39",
                parent_id=ROOT_ITEM_ID,
                name="Attachments 2",
            )

        self.assertEqual(copied.provider_item_id, "copied-id")
        copy_request = mock_urlopen.call_args_list[0].args[0]
        self.assertIn("/drives/remote-drive-id/items/remote-item-id/copy", copy_request.full_url)

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_update_item_resolves_root_parent(self, mock_graph_request):
        mock_graph_request.side_effect = [
            {"id": "drive-root-id"},
            _file_payload(item_id="moved-id", parent_id="drive-root-id"),
        ]

        moved = self.adapter.update_item(
            credentials={"access_token": "token"},
            item_id="moved-id",
            parent_id=ROOT_ITEM_ID,
        )

        self.assertEqual(moved.provider_item_id, "moved-id")
        patch_call = mock_graph_request.call_args_list[-1]
        self.assertEqual(patch_call.kwargs["body"]["parentReference"]["id"], "drive-root-id")

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_delete_item_permanent_uses_graph_endpoint(self, mock_graph_request):
        self.adapter.delete_item(
            credentials={"access_token": "token"},
            item_id="trashed-id",
            permanent=True,
        )

        mock_graph_request.assert_called_once()
        call_args = mock_graph_request.call_args
        self.assertEqual(call_args.args[0], "POST")
        self.assertIn("/permanentDelete", call_args.args[1])

    @patch.object(OneDriveFileAdapter, "_graph_request")
    def test_upload_file_parses_graph_response(self, mock_graph_request):
        payload = _file_payload(item_id="uploaded-id", name="upload.txt")
        mock_graph_request.return_value = json.dumps(payload).encode("utf-8")

        uploaded = self.adapter.upload_file(
            credentials={"access_token": "token"},
            name="upload.txt",
            parent_id=ROOT_ITEM_ID,
            content=b"hello",
            content_type="text/plain",
        )

        self.assertEqual(uploaded.provider_item_id, "uploaded-id")
        upload_call = mock_graph_request.call_args
        self.assertEqual(upload_call.args[0], "PUT")
        self.assertIn(":/upload.txt:/content", upload_call.args[1])
