from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.common.responses import ApiResponse
from apps.common.exceptions.base import AppException

from apps.iam.serializers import LogoutSerializer
from apps.iam.services import TokenService


class LogoutAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LogoutSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:

            TokenService.logout(serializer.validated_data["refresh"])

            return ApiResponse(
                success=True,
                message="Logout successful.",
                data=None,
                status_code=status.HTTP_200_OK,
            )

        except AppException as exc:

            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
