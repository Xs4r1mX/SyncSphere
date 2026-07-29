from django.urls import path

from apps.iam.views import RegisterAPIView

app_name = "iam"

urlpatterns = [
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="register",
    ),
]