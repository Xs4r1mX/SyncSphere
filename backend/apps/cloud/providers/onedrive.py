import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any
from urllib.parse import urlencode

import msal
from django.conf import settings

from apps.common.constants import ProviderType
from apps.common.exceptions import (
    ProviderAuthException,
    ProviderConfigurationException,
)

from .base import CloudProviderAdapter

logger = logging.getLogger(__name__)

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class OneDriveAdapter(CloudProviderAdapter):
    """Microsoft OneDrive OAuth and account metadata adapter."""

    provider_type = ProviderType.ONEDRIVE

    def _ensure_configured(self) -> None:
        if not all(
            [
                settings.ONEDRIVE_OAUTH_CLIENT_ID,
                settings.ONEDRIVE_OAUTH_CLIENT_SECRET,
                settings.ONEDRIVE_OAUTH_REDIRECT_URI,
            ]
        ):
            raise ProviderConfigurationException(
                "OneDrive OAuth credentials are not configured."
            )

    def _authority(self) -> str:
        tenant = settings.ONEDRIVE_OAUTH_TENANT or "common"
        return f"https://login.microsoftonline.com/{tenant}"

    def _msal_app(self) -> msal.ConfidentialClientApplication:
        return msal.ConfidentialClientApplication(
            settings.ONEDRIVE_OAUTH_CLIENT_ID,
            authority=self._authority(),
            client_credential=settings.ONEDRIVE_OAUTH_CLIENT_SECRET,
        )

    @staticmethod
    def _delegated_scopes() -> list[str]:
        return [
            scope
            for scope in settings.ONEDRIVE_OAUTH_SCOPES
            if scope != "offline_access"
        ]

    def _credentials_to_payload(
        self,
        token_response: dict[str, Any],
        *,
        existing_refresh_token: str | None = None,
    ) -> dict[str, Any]:
        access_token = token_response.get("access_token")
        if not access_token:
            raise ProviderAuthException(
                "OneDrive token response did not include an access token."
            )

        expires_in = int(token_response.get("expires_in", 3600))
        expiry = datetime.now(dt_timezone.utc) + timedelta(seconds=expires_in)

        scope_value = token_response.get("scope", "")
        if isinstance(scope_value, str) and scope_value.strip():
            scopes = scope_value.split()
        else:
            scopes = list(settings.ONEDRIVE_OAUTH_SCOPES)

        refresh_token = token_response.get("refresh_token") or existing_refresh_token

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": expiry.isoformat(),
            "scopes": scopes,
        }

    def _token_result_to_payload(
        self,
        result: dict[str, Any],
        *,
        existing_refresh_token: str | None = None,
    ) -> dict[str, Any]:
        if "error" in result:
            logger.warning(
                "OneDrive token request failed",
                extra={
                    "provider": self.provider_type,
                    "error": result.get("error"),
                },
            )
            raise ProviderAuthException(
                result.get("error_description")
                or "OneDrive token request failed."
            )
        return self._credentials_to_payload(
            result,
            existing_refresh_token=existing_refresh_token,
        )

    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        self._ensure_configured()
        params = {
            "client_id": settings.ONEDRIVE_OAUTH_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(settings.ONEDRIVE_OAUTH_SCOPES),
            "state": state,
        }
        return (
            f"{self._authority()}/oauth2/v2.0/authorize?"
            f"{urlencode(params)}"
        )

    def exchange_code(self, *, code: str, redirect_uri: str) -> dict[str, Any]:
        self._ensure_configured()

        result = self._msal_app().acquire_token_by_authorization_code(
            code,
            scopes=self._delegated_scopes(),
            redirect_uri=redirect_uri,
        )
        payload = self._token_result_to_payload(result)
        identity = self.get_account_identity(credentials=payload)
        quota = self.get_quota(credentials=payload)

        return {
            "credentials": payload,
            "identity": identity,
            "quota": quota,
            "scopes": payload["scopes"],
        }

    def refresh_access_token(self, *, refresh_token: str) -> dict[str, Any]:
        self._ensure_configured()

        result = self._msal_app().acquire_token_by_refresh_token(
            refresh_token,
            scopes=self._delegated_scopes(),
        )
        return self._token_result_to_payload(
            result,
            existing_refresh_token=refresh_token,
        )

    def revoke_credentials(self, *, credentials: dict[str, Any]) -> None:
        access_token = credentials.get("access_token")
        if not access_token:
            return

        logger.info(
            "OneDrive unlink completed; token revoke is best-effort only",
            extra={"provider": self.provider_type},
        )

    def get_account_identity(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        profile = _graph_get(
            "/me",
            access_token=credentials.get("access_token", ""),
        )

        account_id = profile.get("id")
        email = profile.get("mail") or profile.get("userPrincipalName") or ""
        display_name = profile.get("displayName") or email or "OneDrive"

        if not account_id:
            raise ProviderAuthException(
                "OneDrive account identity response was incomplete."
            )

        return {
            "provider_account_id": str(account_id),
            "account_email": email,
            "display_name_hint": display_name,
        }

    def get_quota(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        drive = _graph_get(
            "/me/drive?$select=quota",
            access_token=credentials.get("access_token", ""),
        )
        quota = drive.get("quota") or {}

        total = quota.get("total")
        used = quota.get("used")

        return {
            "quota_total_bytes": int(total) if total is not None else None,
            "quota_used_bytes": int(used) if used is not None else None,
        }


def _graph_get(path: str, *, access_token: str) -> dict[str, Any]:
    import json
    import urllib.error
    import urllib.request

    if not access_token:
        raise ProviderAuthException("Missing access token for Microsoft Graph.")

    url = path if path.startswith("http") else f"{GRAPH_BASE_URL}{path}"
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        logger.warning(
            "Microsoft Graph request failed",
            extra={"status_code": exc.code, "path": path},
        )
        raise ProviderAuthException(
            "Failed to fetch data from Microsoft Graph."
        ) from exc
    except urllib.error.URLError as exc:
        logger.warning(
            "Microsoft Graph request failed",
            extra={"path": path},
        )
        raise ProviderAuthException(
            "Failed to fetch data from Microsoft Graph."
        ) from exc
