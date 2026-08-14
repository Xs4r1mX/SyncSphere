import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any

import dropbox
from django.conf import settings

from apps.common.constants import ProviderType
from apps.common.exceptions import (
    ProviderAuthException,
    ProviderConfigurationException,
)

from .base import CloudProviderAdapter

logger = logging.getLogger(__name__)

DROPBOX_AUTHORIZE_URI = "https://www.dropbox.com/oauth2/authorize"
DROPBOX_TOKEN_URI = "https://api.dropbox.com/oauth2/token"


class DropboxAdapter(CloudProviderAdapter):
    """Dropbox OAuth and account metadata adapter."""

    provider_type = ProviderType.DROPBOX

    def _ensure_configured(self) -> None:
        if not all(
            [
                settings.DROPBOX_OAUTH_APP_KEY,
                settings.DROPBOX_OAUTH_APP_SECRET,
                settings.DROPBOX_OAUTH_REDIRECT_URI,
            ]
        ):
            raise ProviderConfigurationException(
                "Dropbox OAuth credentials are not configured."
            )

    def _credentials_to_payload(
        self,
        token_response: dict[str, Any],
        *,
        existing_refresh_token: str | None = None,
    ) -> dict[str, Any]:
        expires_in = int(token_response.get("expires_in", 14400))
        expiry = datetime.now(dt_timezone.utc) + timedelta(seconds=expires_in)

        scope_value = token_response.get("scope", "")
        if isinstance(scope_value, str) and scope_value.strip():
            scopes = scope_value.split()
        else:
            scopes = list(settings.DROPBOX_OAUTH_SCOPES)

        refresh_token = token_response.get("refresh_token") or existing_refresh_token

        return {
            "access_token": token_response["access_token"],
            "refresh_token": refresh_token,
            "token_expiry": expiry.isoformat(),
            "scopes": scopes,
        }

    def _client_from_payload(self, credentials: dict[str, Any]) -> dropbox.Dropbox:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ProviderAuthException("Missing access token for Dropbox client.")

        return dropbox.Dropbox(oauth2_access_token=access_token)

    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        self._ensure_configured()
        params = {
            "client_id": settings.DROPBOX_OAUTH_APP_KEY,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "token_access_type": "offline",
            "state": state,
            "scope": " ".join(settings.DROPBOX_OAUTH_SCOPES),
        }
        return f"{DROPBOX_AUTHORIZE_URI}?{urllib.parse.urlencode(params)}"

    def exchange_code(self, *, code: str, redirect_uri: str) -> dict[str, Any]:
        self._ensure_configured()

        try:
            token_response = _post_token(
                {
                    "code": code,
                    "grant_type": "authorization_code",
                    "client_id": settings.DROPBOX_OAUTH_APP_KEY,
                    "client_secret": settings.DROPBOX_OAUTH_APP_SECRET,
                    "redirect_uri": redirect_uri,
                }
            )
        except urllib.error.HTTPError as exc:
            logger.warning(
                "Dropbox OAuth code exchange failed",
                extra={
                    "provider": self.provider_type,
                    "status_code": exc.code,
                },
            )
            raise ProviderAuthException(
                "Failed to exchange authorization code with Dropbox."
            ) from exc
        except urllib.error.URLError as exc:
            logger.warning(
                "Dropbox OAuth code exchange request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to exchange authorization code with Dropbox."
            ) from exc

        payload = self._credentials_to_payload(token_response)
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

        try:
            token_response = _post_token(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.DROPBOX_OAUTH_APP_KEY,
                    "client_secret": settings.DROPBOX_OAUTH_APP_SECRET,
                }
            )
        except urllib.error.HTTPError as exc:
            logger.warning(
                "Dropbox token refresh failed",
                extra={
                    "provider": self.provider_type,
                    "status_code": exc.code,
                },
            )
            raise ProviderAuthException(
                "Failed to refresh Dropbox access token."
            ) from exc
        except urllib.error.URLError as exc:
            logger.warning(
                "Dropbox token refresh request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to refresh Dropbox access token."
            ) from exc

        return self._credentials_to_payload(
            token_response,
            existing_refresh_token=refresh_token,
        )

    def revoke_credentials(self, *, credentials: dict[str, Any]) -> None:
        access_token = credentials.get("access_token")
        if not access_token:
            return

        try:
            client = self._client_from_payload(credentials)
            client.auth_token_revoke()
        except dropbox.exceptions.AuthError:
            logger.warning(
                "Dropbox token revoke returned auth error",
                extra={"provider": self.provider_type},
            )
        except dropbox.exceptions.ApiError:
            logger.warning(
                "Dropbox token revoke request failed",
                extra={"provider": self.provider_type},
            )

    def get_account_identity(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        try:
            client = self._client_from_payload(credentials)
            account = client.users_get_current_account()
        except dropbox.exceptions.AuthError as exc:
            logger.warning(
                "Dropbox account identity request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to fetch Dropbox account identity."
            ) from exc
        except dropbox.exceptions.ApiError as exc:
            logger.warning(
                "Dropbox account identity request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to fetch Dropbox account identity."
            ) from exc

        account_id = account.account_id
        email = account.email or ""
        name = account.name.display_name if account.name else email or "Dropbox"

        if not account_id:
            raise ProviderAuthException(
                "Dropbox account identity response was incomplete."
            )

        return {
            "provider_account_id": str(account_id),
            "account_email": email,
            "display_name_hint": name,
        }

    def get_quota(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        try:
            client = self._client_from_payload(credentials)
            usage = client.users_get_space_usage()
        except dropbox.exceptions.AuthError as exc:
            logger.warning(
                "Dropbox quota request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to fetch Dropbox storage quota."
            ) from exc
        except dropbox.exceptions.ApiError as exc:
            logger.warning(
                "Dropbox quota request failed",
                extra={"provider": self.provider_type},
            )
            raise ProviderAuthException(
                "Failed to fetch Dropbox storage quota."
            ) from exc

        total = _parse_allocation_total(usage.allocation)
        used = usage.used

        return {
            "quota_total_bytes": int(total) if total is not None else None,
            "quota_used_bytes": int(used) if used is not None else None,
        }


def _parse_allocation_total(allocation) -> int | None:
    """Extract total bytes from Dropbox SpaceAllocation union."""
    if allocation.is_individual():
        return allocation.get_individual().allocated
    if allocation.is_team():
        team = allocation.get_team()
        return team.user_within_team_space_allocated or team.allocated
    return None


def _post_token(data: dict[str, str]) -> dict[str, Any]:
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(
        DROPBOX_TOKEN_URI,
        data=encoded,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
