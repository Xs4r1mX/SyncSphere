from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.common.responses import ApiResponse
from apps.iam.services import VerificationService


class VerifyEmailAPIView(APIView):

    permission_classes = [
        AllowAny
    ]


    def get(self, request, token):

        try:

            user = (
                VerificationService
                .verify_email_token(
                    token
                )
            )


            return ApiResponse(
                success=True,
                message="Email verified successfully.",
                data={
                    "email": user.email
                },
                status_code=status.HTTP_200_OK,
            )


        except ValueError as error:

            return ApiResponse(
                success=False,
                message=str(error),
                status_code=status.HTTP_400_BAD_REQUEST,
            )