from rest_framework import status

from .base import AppException


class IncorrectPasswordException(AppException):

    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Incorrect password."


class UserNotFoundException(AppException):

    status_code = status.HTTP_404_NOT_FOUND
    default_message = "User not found."


class EmailNotVerifiedException(AppException):

    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Please verify your email first."


class InactiveUserException(AppException):

    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Your account has been deactivated."


class InvalidVerificationTokenException(AppException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Invalid verification token."


class InvalidPasswordResetTokenException(AppException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Invalid password reset token."


class EmailAlreadyVerifiedException(AppException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Email is already verified."


class VerificationTokenExpiredException(AppException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Verification token has expired."


class InvalidRefreshTokenException(AppException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Invalid refresh token."
