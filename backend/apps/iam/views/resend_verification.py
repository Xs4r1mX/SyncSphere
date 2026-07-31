from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.conf import settings

from apps.iam.serializers import ResendVerificationSerializer

from apps.iam.services import VerificationService

from apps.iam.services import VerificationService
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

            VerificationService.send_verification_email(user, token)

        except Exception as e:
            return ApiResponse(
                success=False,
                message=str(e),
                status_code=getattr(e, "status_code", 500),
            )

        return ApiResponse(
            success=True,
            message="Verification email sent again.",
            status_code=status.HTTP_200_OK,
        )
