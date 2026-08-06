import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone as dt_timezone
from typing import Any

import google.auth.exceptions
from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from apps.common.constants import ProviderType
from apps.common.exceptions import (
    ProviderAuthException,
    ProviderConfigurationException,
)

from .base import CloudProviderAdapter

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URI = "https://oauth2.googleapis.com/revoke"
GOOGLE_USERINFO_URI = "https://www.googleapis.com/oauth2/v2/userinfo"


class GoogleDriveAdapter(CloudProviderAdapter):
    """Google Drive OAuth and account metadata adapter."""

    provider_type = ProviderType.GOOGLE_DRIVE

    def _ensure_configured(self) -> None:
        if not all(
            [
                settings.GOOGLE_OAUTH_CLIENT_ID,
                settings.GOOGLE_OAUTH_CLIENT_SECRET,
                settings.GOOGLE_OAUTH_REDIRECT_URI,
            ]
        ):
            raise ProviderConfigurationException(
                "Google OAuth credentials are not configured."
            )

    def _client_config(self) -> dict[str, Any]:
        self._ensure_configured()
        return {
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": GOOGLE_TOKEN_URI,
                "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
            }
        }

    def _build_flow(self, *, redirect_uri: str | None = None) -> Flow:
        return Flow.from_client_config(
            self._client_config(),
            scopes=settings.GOOGLE_OAUTH_SCOPES,
            redirect_uri=redirect_uri or settings.GOOGLE_OAUTH_REDIRECT_URI,
        )

    @staticmethod
    def _credentials_to_payload(credentials: Credentials) -> dict[str, Any]:
        expiry = credentials.expiry
        token_expiry = None
        if expiry is not None:
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=dt_timezone.utc)
            token_expiry = expiry.astimezone(dt_timezone.utc).isoformat()

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": token_expiry,
            "scopes": list(credentials.scopes or settings.GOOGLE_OAUTH_SCOPES),
        }

    def _credentials_from_payload(self, payload: dict[str, Any]) -> Credentials:
        self._ensure_configured()

        expiry = None
        token_expiry = payload.get("token_expiry")
        if token_expiry:
            expiry = datetime.fromisoformat(token_expiry)

        return Credentials(
            token=payload.get("access_token"),
            refresh_token=payload.get("refresh_token"),
            token_uri=GOOGLE_TOKEN_URI,
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
            scopes=payload.get("scopes") or settings.GOOGLE_OAUTH_SCOPES,
            expiry=expiry,
        )

    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        flow = self._build_flow(redirect_uri=redirect_uri)
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes=True,
            prompt="consent",
            state=state,
        )
        return authorization_url

    def exchange_code(self, *, code: str, redirect_uri: str) -> dict[str, Any]:
        try:
            flow = self._build_flow(redirect_uri=redirect_uri)
            flow.fetch_token(code=code)
        except Exception as exc:
            logger.warning(
                "Google OAuth code exchange failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to exchange authorization code with Google."
            ) from exc

        credentials = flow.credentials
        payload = self._credentials_to_payload(credentials)
        identity = self.get_account_identity(credentials=payload)
        quota = self.get_quota(credentials=payload)

        return {
            "credentials": payload,
            "identity": identity,
            "quota": quota,
            "scopes": payload["scopes"],
        }

    def refresh_access_token(self, *, refresh_token: str) -> dict[str, Any]:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=GOOGLE_TOKEN_URI,
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
            scopes=settings.GOOGLE_OAUTH_SCOPES,
        )

        try:
            credentials.refresh(Request())
        except google.auth.exceptions.RefreshError as exc:
            logger.warning(
                "Google token refresh failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to refresh Google access token."
            ) from exc

        return self._credentials_to_payload(credentials)

    def revoke_credentials(self, *, credentials: dict[str, Any]) -> None:
        token = credentials.get("access_token") or credentials.get("refresh_token")
        if not token:
            return

        try:
            _post_form(GOOGLE_REVOKE_URI, {"token": token})
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                logger.warning(
                    "Google token revoke returned unexpected status",
                    extra={
                        "provider": self.provider_type,
                        "status_code": exc.code,
                    },
                )
        except urllib.error.URLError:
            logger.warning(
                "Google token revoke request failed",
                extra={"provider": self.provider_type},
            )

    def get_account_identity(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ProviderAuthException("Missing access token for Google account lookup.")

        try:
            profile = _get_json(
                GOOGLE_USERINFO_URI,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except urllib.error.URLError as exc:
            logger.warning(
                "Google userinfo request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to fetch Google account identity."
            ) from exc

        account_id = profile.get("id") or profile.get("sub")
        email = profile.get("email", "")
        name = profile.get("name") or email or "Google Drive"

        if not account_id:
            raise ProviderAuthException(
                "Google account identity response was incomplete."
            )

        return {
            "provider_account_id": str(account_id),
            "account_email": email,
            "display_name_hint": name,
        }

    def get_quota(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        google_credentials = self._credentials_from_payload(credentials)

        try:
            service = build(
                "drive",
                "v3",
                credentials=google_credentials,
                cache_discovery=False,
            )
            about = service.about().get(fields="storageQuota").execute()
            storage_quota = about.get("storageQuota", {})
        except (HttpError, google.auth.exceptions.GoogleAuthError) as exc:
            logger.warning(
                "Google Drive quota request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to fetch Google Drive storage quota."
            ) from exc

        return {
            "quota_total_bytes": _parse_optional_int(storage_quota.get("limit")),
            "quota_used_bytes": _parse_optional_int(storage_quota.get("usage")),
        }


def _parse_optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _post_form(url: str, data: dict[str, str]) -> None:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=encoded, method="POST")
    with urllib.request.urlopen(request, timeout=10):
        return


def _get_json(url: str, *, headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
