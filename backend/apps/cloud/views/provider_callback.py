from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.cloud.serializers import CloudConnectionSerializer, OAuthCallbackSerializer
from apps.cloud.services import OAuthConnectionService
from apps.common.exceptions.base import AppException
from apps.common.responses import ApiResponse


class ProviderCallbackAPIView(APIView):
    """
    Completes OAuth for a cloud provider.

    POST: SPA flow — authenticated user submits code + state.
    GET:  Provider redirect — resolves user from state, then redirects to frontend.
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request, provider):
        serializer = OAuthCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            connection = OAuthConnectionService.complete_authorization(
                user=request.user,
                provider=provider,
                code=serializer.validated_data["code"],
                state=serializer.validated_data["state"],
            )
            return ApiResponse(
                success=True,
                message="Cloud account connected successfully.",
                data=CloudConnectionSerializer(connection).data,
                status_code=status.HTTP_201_CREATED,
            )
        except AppException as exc:
            return ApiResponse(
                success=False,
                message=str(exc),
                status_code=getattr(exc, "status_code", 500),
            )

    def get(self, request, provider):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        if error:
            return HttpResponseRedirect(
                _build_frontend_redirect(
                    settings.CLOUD_OAUTH_ERROR_URL,
                    {"error": error},
                )
            )

        if not code or not state:
            return HttpResponseRedirect(
                _build_frontend_redirect(
                    settings.CLOUD_OAUTH_ERROR_URL,
                    {"error": "missing_code_or_state"},
                )
            )

        try:
            connection = OAuthConnectionService.complete_authorization_from_redirect(
                provider=provider,
                code=code,
                state=state,
            )
            return HttpResponseRedirect(
                _build_frontend_redirect(
                    settings.CLOUD_OAUTH_SUCCESS_URL,
                    {"connection_uuid": str(connection.uuid)},
                )
            )
        except AppException as exc:
            return HttpResponseRedirect(
                _build_frontend_redirect(
                    settings.CLOUD_OAUTH_ERROR_URL,
                    {"error": str(exc)},
                )
            )


def _build_frontend_redirect(base_url: str, params: dict[str, str]) -> str:
    query = urlencode(params)
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{query}"
