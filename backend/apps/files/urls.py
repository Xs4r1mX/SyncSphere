from django.urls import path

from apps.files.views import (
    FileBreadcrumbAPIView,
    FileCopyAPIView,
    FileCreateFolderAPIView,
    FileDetailAPIView,
    FileDownloadAPIView,
    FileListAPIView,
    FileOpenAPIView,
    FileQuotaAPIView,
    FileRestoreAPIView,
    FileUploadAPIView,
)

app_name = "files"

urlpatterns = [
    path(
        "<uuid:connection_uuid>/upload/",
        FileUploadAPIView.as_view(),
        name="file-upload",
    ),
    path(
        "<uuid:connection_uuid>/folders/",
        FileCreateFolderAPIView.as_view(),
        name="folder-create",
    ),
    path(
        "<uuid:connection_uuid>/breadcrumb/",
        FileBreadcrumbAPIView.as_view(),
        name="file-breadcrumb",
    ),
    path(
        "<uuid:connection_uuid>/quota/",
        FileQuotaAPIView.as_view(),
        name="file-quota",
    ),
    path(
        "<uuid:connection_uuid>/<path:item_id>/download/",
        FileDownloadAPIView.as_view(),
        name="file-download",
    ),
    path(
        "<uuid:connection_uuid>/<path:item_id>/open/",
        FileOpenAPIView.as_view(),
        name="file-open",
    ),
    path(
        "<uuid:connection_uuid>/<path:item_id>/copy/",
        FileCopyAPIView.as_view(),
        name="file-copy",
    ),
    path(
        "<uuid:connection_uuid>/<path:item_id>/restore/",
        FileRestoreAPIView.as_view(),
        name="file-restore",
    ),
    path(
        "<uuid:connection_uuid>/<path:item_id>/",
        FileDetailAPIView.as_view(),
        name="file-detail",
    ),
    path(
        "<uuid:connection_uuid>/",
        FileListAPIView.as_view(),
        name="file-list",
    ),
]
