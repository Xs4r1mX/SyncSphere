from django.urls import path

from apps.transfers.views import (
    TransferCancelAPIView,
    TransferDetailAPIView,
    TransferItemListAPIView,
    TransferListCreateAPIView,
)

app_name = "transfers"

urlpatterns = [
    path("", TransferListCreateAPIView.as_view(), name="transfer-list-create"),
    path(
        "<uuid:job_uuid>/",
        TransferDetailAPIView.as_view(),
        name="transfer-detail",
    ),
    path(
        "<uuid:job_uuid>/items/",
        TransferItemListAPIView.as_view(),
        name="transfer-items",
    ),
    path(
        "<uuid:job_uuid>/cancel/",
        TransferCancelAPIView.as_view(),
        name="transfer-cancel",
    ),
]
