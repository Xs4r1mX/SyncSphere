from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.iam.serializers import RegisterSerializer, UserSerializer
from apps.iam.services import AuthService
from apps.common.responses import ApiResponse
from django.conf import settings

from apps.notification.services.email_service import EmailService


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:

            user = AuthService.register_user(**serializer.validated_data)

            return ApiResponse(
                success=True,
                message="User registered successfully.",
                data=UserSerializer(user).data,
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as error:
            return ApiResponse(
                success=False,
                message=str(error),
                status_code=getattr(error, "status_code", 500),
            )
