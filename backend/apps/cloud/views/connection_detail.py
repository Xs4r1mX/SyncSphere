from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cloud.serializers import (
    CloudConnectionSerializer,
    UpdateConnectionSerializer,
)
from apps.cloud.services import ConnectionService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class CloudConnectionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid):
        try:
            connection = ConnectionService.get_connection(
                user=request.user,
                connection_uuid=connection_uuid,
            )
            serializer = CloudConnectionSerializer(connection)
            return ApiResponse(
                success=True,
                message="Cloud connection fetched successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )

    def patch(self, request, connection_uuid):
        serializer = UpdateConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            connection = ConnectionService.update_display_name(
                user=request.user,
                connection_uuid=connection_uuid,
                display_name=serializer.validated_data["display_name"],
            )
            return ApiResponse(
                success=True,
                message="Cloud connection updated successfully.",
                data=CloudConnectionSerializer(connection).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
