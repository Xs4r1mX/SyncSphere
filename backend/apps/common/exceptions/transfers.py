from rest_framework import status

from .base import AppException


class TransferException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "A transfer error occurred."


class TransferNotFoundException(TransferException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Transfer job not found."


class TransferInvalidStateException(TransferException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Transfer job cannot be modified in its current state."


class TransferOperationMismatchException(TransferException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Transfer operation does not match the source item type."


class TransferTooLargeException(TransferException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_message = "Transfer exceeds the maximum allowed size."


class TransferConflictException(TransferException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "A file or folder with this name already exists at the destination."


class TransferSourceCleanupException(TransferException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_message = (
        "Destination write succeeded but source cleanup failed. "
        "Data was not lost."
    )
