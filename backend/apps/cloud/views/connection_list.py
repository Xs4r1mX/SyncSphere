from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cloud.serializers import CloudConnectionSerializer
from apps.cloud.services import ConnectionService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class CloudConnectionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            connections = ConnectionService.list_connections(user=request.user)
            serializer = CloudConnectionSerializer(connections, many=True)
            return ApiResponse(
                success=True,
                message="Cloud connections fetched successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
