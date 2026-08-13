from rest_framework import status

from .base import AppException


class ActivityException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "An activity error occurred."


class ActivityNotFoundException(ActivityException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Activity log entry not found."
