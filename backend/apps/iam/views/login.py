from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.common.responses import ApiResponse

from apps.iam.serializers import LoginSerializer
from apps.iam.services import AuthService
from apps.iam.serializers import UserSerializer


class LoginAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:

            user = AuthService.authenticate_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            tokens = AuthService.generate_tokens(user)

            return ApiResponse(
                success=True,
                message="Login successful.",
                data={
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                    "user": UserSerializer(user).data,
                },
                status_code=status.HTTP_200_OK,
            )

        except Exception as error:

            return ApiResponse(
                success=False,
                message=str(error),
                status_code=getattr(error, "status_code", 500),
            )
