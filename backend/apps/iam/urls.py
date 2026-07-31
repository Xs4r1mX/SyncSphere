from django.urls import path

from apps.iam.views import (
    RegisterAPIView,
    VerifyEmailAPIView,
    ResendVerificationAPIView,
    LoginAPIView,
    RefreshTokenAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
)

app_name = "iam"

urlpatterns = [
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="register",
    ),
    path(
        "verify-email/<str:token>/",
        VerifyEmailAPIView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification/",
        ResendVerificationAPIView.as_view(),
        name="resend-verification",
    ),
    path(
        "login/",
        LoginAPIView.as_view(),
        name="login",
    ),
    path(
        "refresh/",
        RefreshTokenAPIView.as_view(),
        name="refresh-token",
    ),
    path(
        "logout/",
        LogoutAPIView.as_view(),
        name="logout",
    ),
    path(
        "me/",
        CurrentUserAPIView.as_view(),
        name="current-user",
    ),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path(
        "forgot-password/",
        ForgotPasswordAPIView.as_view(),
        name="forgot-password",
    ),
    path(
        "reset-password/",
        ResetPasswordAPIView.as_view(),
        name="reset-password",
    ),
]
