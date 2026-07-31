from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status


from apps.common.responses import ApiResponse

from apps.iam.serializers import (
    ForgotPasswordSerializer,
)

from apps.iam.services import (
    PasswordService,
)


class ForgotPasswordAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ForgotPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:

            PasswordService.request_password_reset(serializer.validated_data["email"])

            return ApiResponse(
                success=True,
                message=("A password reset link has been sent."),
                data=None,
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return ApiResponse(
                success=False,
                message=str(e),
                status_code=getattr(e, "status_code", 500),
            )
