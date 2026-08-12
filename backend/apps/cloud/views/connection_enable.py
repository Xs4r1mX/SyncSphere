from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cloud.serializers import CloudConnectionSerializer
from apps.cloud.services import ConnectionService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class CloudConnectionEnableAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, connection_uuid):
        try:
            connection = ConnectionService.enable_connection(
                user=request.user,
                connection_uuid=connection_uuid,
            )
            return ApiResponse(
                success=True,
                message="Cloud connection enabled successfully.",
                data=CloudConnectionSerializer(connection).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
