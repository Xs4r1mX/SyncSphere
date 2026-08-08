from apps.common.constants import ProviderType
from apps.common.exceptions import ProviderNotImplementedException

from .base import CloudFileAdapter


class StubCloudFileAdapter(CloudFileAdapter):
    provider_type: str = ""

    def _raise(self) -> None:
        raise ProviderNotImplementedException()

    def list_items(self, **kwargs):
        self._raise()

    def get_item(self, **kwargs):
        self._raise()

    def create_folder(self, **kwargs):
        self._raise()

    def upload_file(self, **kwargs):
        self._raise()

    def download_file(self, **kwargs):
        self._raise()

    def update_item(self, **kwargs):
        self._raise()

    def delete_item(self, **kwargs):
        self._raise()

    def copy_item(self, **kwargs):
        self._raise()

    def restore_item(self, **kwargs):
        self._raise()

    def get_breadcrumb(self, **kwargs):
        self._raise()

    def get_quota(self, **kwargs):
        self._raise()


class DropboxFileStubAdapter(StubCloudFileAdapter):
    provider_type = ProviderType.DROPBOX


class OneDriveFileStubAdapter(StubCloudFileAdapter):
    provider_type = ProviderType.ONEDRIVE
