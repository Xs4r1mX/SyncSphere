from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.files"
    label = "files"
    verbose_name = "Files"

    def ready(self):
        from apps.files.providers.factory import FileProviderFactory
        from apps.files.providers.dropbox import DropboxFileAdapter
        from apps.files.providers.google_drive import GoogleDriveFileAdapter
        from apps.files.providers.onedrive import OneDriveFileAdapter

        FileProviderFactory.register(GoogleDriveFileAdapter)
        FileProviderFactory.register(DropboxFileAdapter)
        FileProviderFactory.register(OneDriveFileAdapter)
