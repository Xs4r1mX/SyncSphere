from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cloud.serializers import ConnectionHealthSerializer
from apps.cloud.services import ConnectionHealthService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class CloudConnectionHealthAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid):
        try:
            health = ConnectionHealthService.check_health(
                user=request.user,
                connection_uuid=connection_uuid,
            )
            serializer = ConnectionHealthSerializer(health)
            return ApiResponse(
                success=True,
                message="Connection health checked successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
