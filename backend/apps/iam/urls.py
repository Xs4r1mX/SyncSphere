from django.urls import path

from apps.iam.views import RegisterAPIView, VerifyEmailAPIView, ResendVerificationAPIView, LoginAPIView

app_name = "iam"

urlpatterns = [
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="register",
    ),
    path(
        "verify-email/<uuid:token>/",
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
]