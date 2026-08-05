from apps.common.constants import ProviderType

from .base import StubCloudProviderAdapter


class GoogleDriveStubAdapter(StubCloudProviderAdapter):
    provider_type = ProviderType.GOOGLE_DRIVE


class DropboxStubAdapter(StubCloudProviderAdapter):
    provider_type = ProviderType.DROPBOX


class OneDriveStubAdapter(StubCloudProviderAdapter):
    provider_type = ProviderType.ONEDRIVE
