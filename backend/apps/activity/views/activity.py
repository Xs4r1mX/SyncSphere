from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.activity.serializers import (
    ActivityListQuerySerializer,
    ActivityLogSerializer,
)
from apps.activity.services import ActivityService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class ActivityListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = ActivityListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = query.validated_data

        try:
            result = ActivityService.list_activity(
                user=request.user,
                action=data.get("action"),
                resource_type=data.get("resource_type"),
                connection_uuid=data.get("connection_uuid"),
                provider=data.get("provider"),
                created_after=data.get("created_after"),
                created_before=data.get("created_before"),
                limit=data.get("limit", 50),
                offset=data.get("offset", 0),
            )
            return ApiResponse(
                success=True,
                message="Activity fetched successfully.",
                data={
                    "items": ActivityLogSerializer(result["items"], many=True).data,
                    "limit": result["limit"],
                    "offset": result["offset"],
                    "total": result["total"],
                },
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class ActivityDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, activity_uuid):
        try:
            entry = ActivityService.get_activity(
                user=request.user,
                activity_uuid=activity_uuid,
            )
            return ApiResponse(
                success=True,
                message="Activity fetched successfully.",
                data=ActivityLogSerializer(entry).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
