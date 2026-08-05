from rest_framework import status

from .base import AppException


class CloudException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "A cloud storage error occurred."


class ConnectionNotFoundException(CloudException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Cloud connection not found."


class ConnectionAccessDeniedException(CloudException):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "You do not have access to this cloud connection."


class ConnectionAlreadyExistsException(CloudException):
    status_code = status.HTTP_409_CONFLICT
    default_message = "This cloud account is already connected."


class ConnectionDisabledException(CloudException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "This cloud connection is disabled."


class InvalidProviderException(CloudException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Unsupported cloud storage provider."


class ProviderNotImplementedException(CloudException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_message = "This cloud provider is not implemented yet."


class CredentialEncryptionException(CloudException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Failed to process stored credentials."
