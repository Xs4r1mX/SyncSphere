from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.files"
    label = "files"
    verbose_name = "Files"

    def ready(self):
        from apps.files.providers.factory import FileProviderFactory
        from apps.files.providers.google_drive import GoogleDriveFileAdapter
        from apps.files.providers.stubs import (
            DropboxFileStubAdapter,
            OneDriveFileStubAdapter,
        )

        FileProviderFactory.register(GoogleDriveFileAdapter)
        FileProviderFactory.register(DropboxFileStubAdapter)
        FileProviderFactory.register(OneDriveFileStubAdapter)
