from django.urls import path

from apps.activity.views import ActivityDetailAPIView, ActivityListAPIView

app_name = "activity"

urlpatterns = [
    path("", ActivityListAPIView.as_view(), name="activity-list"),
    path(
        "<uuid:activity_uuid>/",
        ActivityDetailAPIView.as_view(),
        name="activity-detail",
    ),
]
