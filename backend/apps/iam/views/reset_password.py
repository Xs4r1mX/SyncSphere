from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status


from apps.iam.serializers import (
    ResetPasswordSerializer,
)

from apps.iam.services import (
    PasswordService,
)

from apps.common.responses import (
    ApiResponse,
)


class ResetPasswordAPIView(APIView):

    permission_classes = [AllowAny]

    def post(
        self,
        request,
    ):

        serializer = ResetPasswordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        PasswordService.reset_password(
            token=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )

        return ApiResponse(
            success=True,
            message=("Password reset successfully."),
            data=None,
            status_code=status.HTTP_200_OK,
        )
