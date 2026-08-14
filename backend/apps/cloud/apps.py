from django.apps import AppConfig


class CloudConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cloud"
    label = "cloud"
    verbose_name = "Cloud Connections"

    def ready(self):
        from apps.cloud.providers.factory import ProviderFactory
        from apps.cloud.providers.dropbox import DropboxAdapter
        from apps.cloud.providers.google_drive import GoogleDriveAdapter
        from apps.cloud.providers.stubs import OneDriveStubAdapter

        ProviderFactory.register(GoogleDriveAdapter)
        ProviderFactory.register(DropboxAdapter)
        ProviderFactory.register(OneDriveStubAdapter)
