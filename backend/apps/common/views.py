from rest_framework import status
from rest_framework.views import APIView

from apps.common.responses import ApiResponse
from apps.common.services import WorkerHealthService


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return ApiResponse(
            success=True,
            message="Service is healthy.",
            data={
                "status": "ok",
                "service": "sync-sphere-backend",
                "version": "v1",
                "request_id": getattr(request, "request_id", None),
            },
            status_code=status.HTTP_200_OK,
        )


class WorkerHealthCheckView(APIView):
    """Broker and Celery worker readiness probe."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        payload = WorkerHealthService.check()
        http_status = (
            status.HTTP_200_OK
            if payload["broker"]["ok"]
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return ApiResponse(
            success=payload["broker"]["ok"],
            message=(
                "Worker infrastructure is reachable."
                if payload["broker"]["ok"]
                else "Celery broker is unreachable."
            ),
            data=payload,
            status_code=http_status,
        )
