from rest_framework import status

from .base import AppException


class FileOperationException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "A file operation error occurred."


class FileNotFoundException(FileOperationException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "File or folder not found."


class FilePermissionDeniedException(FileOperationException):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "You do not have permission to access this file or folder."


class FileConflictException(FileOperationException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "A file or folder with this name already exists."


class InvalidFileOperationException(FileOperationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Invalid file operation request."


class FileUploadTooLargeException(FileOperationException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_message = "Uploaded file exceeds the maximum allowed size."


class InsufficientStorageException(FileOperationException):
    status_code = status.HTTP_507_INSUFFICIENT_STORAGE
    default_message = "Not enough storage space available."


class ProviderRateLimitedException(FileOperationException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Cloud provider rate limit exceeded. Please try again later."
