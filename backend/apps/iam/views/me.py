from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from apps.common.responses import ApiResponse
from apps.iam.serializers import UserSerializer


class CurrentUserAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return ApiResponse(
            success=True,
            message="User fetched successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )
