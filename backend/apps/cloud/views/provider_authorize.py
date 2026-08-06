from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cloud.services import OAuthConnectionService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class ProviderAuthorizeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, provider):
        try:
            payload = OAuthConnectionService.start_authorization(
                user=request.user,
                provider=provider,
            )
            return ApiResponse(
                success=True,
                message="Authorization URL generated successfully.",
                data=payload,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
