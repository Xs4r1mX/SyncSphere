from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.iam.serializers import RegisterSerializer, UserSerializer
from apps.iam.services import AuthService
from apps.common.responses import ApiResponse


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:

            user = AuthService.register_user(**serializer.validated_data)

            return ApiResponse(
                success=True,
                message=(
                    "User registered successfully. "
                    "Please verify your email to activate your account."
                ),
                data=UserSerializer(user).data,
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as error:
            return ApiResponse(
                success=False,
                message=str(error),
                status_code=getattr(error, "status_code", 500),
            )
