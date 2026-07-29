from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.iam.serializers import ResendVerificationSerializer

from apps.iam.services import VerificationService

from apps.notification.services import EmailService
from apps.common.responses.api_response import ApiResponse


class ResendVerificationAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResendVerificationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            user, token = VerificationService.regenerate_verification_token(
                serializer.validated_data["email"]
            )

            verification_url = f"http://localhost:3000/" f"verify-email/{token.token}"

            EmailService.send_verification_email(
                user=user,
                verification_url=verification_url,
            )

        except ValueError as e:
            return ApiResponse(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return ApiResponse(
            success=True,
            message="Verification email sent again.",
            status_code=status.HTTP_200_OK,
        )
