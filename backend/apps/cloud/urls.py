from django.urls import path

from apps.cloud.views import (
    CloudConnectionDetailAPIView,
    CloudConnectionDisableAPIView,
    CloudConnectionListAPIView,
)

app_name = "cloud"

urlpatterns = [
    path(
        "connections/",
        CloudConnectionListAPIView.as_view(),
        name="connection-list",
    ),
    path(
        "connections/<uuid:connection_uuid>/",
        CloudConnectionDetailAPIView.as_view(),
        name="connection-detail",
    ),
    path(
        "connections/<uuid:connection_uuid>/disable/",
        CloudConnectionDisableAPIView.as_view(),
        name="connection-disable",
    ),
]
