from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse
from apps.files.serializers import (
    BreadcrumbQuerySerializer,
    BreadcrumbSerializer,
    CopyItemSerializer,
    CreateFolderSerializer,
    DeleteItemQuerySerializer,
    FileItemSerializer,
    FileListQuerySerializer,
    FileListSerializer,
    FileUploadSerializer,
    QuotaSummarySerializer,
    UpdateItemSerializer,
)
from apps.files.services import FileService


class FileListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid):

        serializer = FileListQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            result = FileService.list_items(
                user=request.user,
                connection_uuid=connection_uuid,
                parent_id=validated.get("parent_id", "root"),
                page_token=validated.get("page_token"),
                page_size=validated.get("page_size"),
                trashed=validated.get("trashed", False),
            )
            serializer = FileListSerializer(result.to_dict())
            return ApiResponse(
                success=True,
                message="Files fetched successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileQuotaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid):
        try:
            quota = FileService.get_quota(
                user=request.user,
                connection_uuid=connection_uuid,
            )
            serializer = QuotaSummarySerializer(quota.to_dict())
            return ApiResponse(
                success=True,
                message="Storage quota fetched successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileBreadcrumbAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid):
        serializer = BreadcrumbQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            items = FileService.get_breadcrumb(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=validated["item_id"],
            )
            serializer = BreadcrumbSerializer(
                {"items": [item.to_dict() for item in items]}
            )
            return ApiResponse(
                success=True,
                message="Breadcrumb fetched successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileCreateFolderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, connection_uuid):
        serializer = CreateFolderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            item = FileService.create_folder(
                user=request.user,
                connection_uuid=connection_uuid,
                name=validated["name"],
                parent_id=validated.get("parent_id", "root"),
            )
            return ApiResponse(
                success=True,
                message="Folder created successfully.",
                data=FileItemSerializer(item.to_dict()).data,
                status_code=status.HTTP_201_CREATED,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, connection_uuid):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            item = FileService.upload_file(
                user=request.user,
                connection_uuid=connection_uuid,
                name=validated.get("name") or validated["file"].name,
                parent_id=validated.get("parent_id", "root"),
                content=validated["file"].read(),
                content_type=validated["file"].content_type or "application/octet-stream",
            )
            return ApiResponse(
                success=True,
                message="File uploaded successfully.",
                data=FileItemSerializer(item.to_dict()).data,
                status_code=status.HTTP_201_CREATED,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid, item_id):
        try:
            item = FileService.get_item(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=item_id,
            )
            return ApiResponse(
                success=True,
                message="File metadata fetched successfully.",
                data=FileItemSerializer(item.to_dict()).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )

    def patch(self, request, connection_uuid, item_id):
        serializer = UpdateItemSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            item = FileService.update_item(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=item_id,
                name=validated.get("name"),
                parent_id=validated.get("parent_id"),
            )
            return ApiResponse(
                success=True,
                message="File updated successfully.",
                data=FileItemSerializer(item.to_dict()).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )

    def delete(self, request, connection_uuid, item_id):
        serializer = DeleteItemQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            FileService.delete_item(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=item_id,
                permanent=validated.get("permanent", False),
            )
            return ApiResponse(
                success=True,
                message="File deleted successfully.",
                data=None,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, connection_uuid, item_id):
        try:
            download = FileService.download_file(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=item_id,
            )
            response = HttpResponse(
                download.content,
                content_type=download.content_type,
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{download.name}"'
            )
            response["Content-Length"] = str(download.size)
            return response
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileCopyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, connection_uuid, item_id):
        serializer = CopyItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        try:
            item = FileService.copy_item(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=item_id,
                parent_id=validated["parent_id"],
                name=validated.get("name"),
            )
            return ApiResponse(
                success=True,
                message="File copied successfully.",
                data=FileItemSerializer(item.to_dict()).data,
                status_code=status.HTTP_201_CREATED,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )


class FileRestoreAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, connection_uuid, item_id):
        try:
            item = FileService.restore_item(
                user=request.user,
                connection_uuid=connection_uuid,
                item_id=item_id,
            )
            return ApiResponse(
                success=True,
                message="File restored successfully.",
                data=FileItemSerializer(item.to_dict()).data,
                status_code=status.HTTP_200_OK,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )
