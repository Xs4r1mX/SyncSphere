from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from apps.common.responses import ApiResponse
from apps.common.exceptions.base import AppException

from apps.iam.serializers import (
    ChangePasswordSerializer,
)

from apps.iam.services import (
    PasswordService,
)


class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        try:

            PasswordService.change_password(
                user=request.user,
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )

            return ApiResponse(
                success=True,
                message="Password changed successfully.",
                data=None,
                status_code=status.HTTP_200_OK,
            )

        except AppException as exc:

            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
