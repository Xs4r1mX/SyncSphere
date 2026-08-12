from django.urls import path

from apps.cloud.views import (
    CloudConnectionDetailAPIView,
    CloudConnectionDisableAPIView,
    CloudConnectionEnableAPIView,
    CloudConnectionHealthAPIView,
    CloudConnectionListAPIView,
    CloudConnectionUnlinkAPIView,
    ProviderAuthorizeAPIView,
    ProviderCallbackAPIView,
)

app_name = "cloud"

urlpatterns = [
    path(
        "providers/<str:provider>/authorize/",
        ProviderAuthorizeAPIView.as_view(),
        name="provider-authorize",
    ),
    path(
        "providers/<str:provider>/callback/",
        ProviderCallbackAPIView.as_view(),
        name="provider-callback",
    ),
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
    path(
        "connections/<uuid:connection_uuid>/enable/",
        CloudConnectionEnableAPIView.as_view(),
        name="connection-enable",
    ),
    path(
        "connections/<uuid:connection_uuid>/unlink/",
        CloudConnectionUnlinkAPIView.as_view(),
        name="connection-unlink",
    ),
    path(
        "connections/<uuid:connection_uuid>/health/",
        CloudConnectionHealthAPIView.as_view(),
        name="connection-health",
    ),
]
