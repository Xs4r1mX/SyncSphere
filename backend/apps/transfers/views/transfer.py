from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse
from apps.transfers.serializers import (
    CreateTransferSerializer,
    TransferItemSerializer,
    TransferJobSerializer,
    TransferListQuerySerializer,
)
from apps.transfers.services import TransferService


class TransferListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = TransferListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        data = query.validated_data
        try:
            result = TransferService.list_transfers(
                user=request.user,
                status=data.get("status"),
                source_connection_uuid=data.get("source_connection_uuid"),
                dest_connection_uuid=data.get("dest_connection_uuid"),
                operation=data.get("operation"),
                created_after=data.get("created_after"),
                created_before=data.get("created_before"),
                limit=data.get("limit", 50),
                offset=data.get("offset", 0),
            )
            return ApiResponse(
                success=True,
                message="Transfers fetched successfully.",
                data={
                    "items": TransferJobSerializer(result["items"], many=True).data,
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

    def post(self, request):
        serializer = CreateTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            job = TransferService.create_transfer(
                user=request.user,
                operation=data["operation"],
                source_connection_uuid=data["source_connection_uuid"],
                dest_connection_uuid=data["dest_connection_uuid"],
                source_item_id=data["source_item_id"],
                dest_parent_id=data.get("dest_parent_id", "root"),
                conflict_policy=data.get("conflict_policy"),
                request_id=getattr(request, "request_id", None),
            )
            return ApiResponse(
                success=True,
                message="Transfer job enqueued successfully.",
                data=TransferJobSerializer(job).data,
                status_code=status.HTTP_202_ACCEPTED,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class TransferDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_uuid):
        try:
            job = TransferService.get_transfer(user=request.user, job_uuid=job_uuid)
            return ApiResponse(
                success=True,
                message="Transfer job fetched successfully.",
                data=TransferJobSerializer(job).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class TransferItemListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_uuid):
        try:
            items = TransferService.list_items(user=request.user, job_uuid=job_uuid)
            return ApiResponse(
                success=True,
                message="Transfer items fetched successfully.",
                data=TransferItemSerializer(items, many=True).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class TransferCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_uuid):
        try:
            job = TransferService.cancel_transfer(
                user=request.user,
                job_uuid=job_uuid,
            )
            return ApiResponse(
                success=True,
                message="Transfer cancellation requested.",
                data=TransferJobSerializer(job).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
