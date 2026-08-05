from django.apps import AppConfig


class CloudConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cloud"
    label = "cloud"
    verbose_name = "Cloud Connections"

    def ready(self):
        from apps.cloud.providers.factory import ProviderFactory
        from apps.cloud.providers.stubs import (
            DropboxStubAdapter,
            GoogleDriveStubAdapter,
            OneDriveStubAdapter,
        )

        ProviderFactory.register(GoogleDriveStubAdapter)
        ProviderFactory.register(DropboxStubAdapter)
        ProviderFactory.register(OneDriveStubAdapter)
