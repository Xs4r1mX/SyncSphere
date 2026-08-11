from django.urls import path

from .views import HealthCheckView, WorkerHealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path(
        "health/workers/",
        WorkerHealthCheckView.as_view(),
        name="worker-health-check",
    ),
]
