from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.cloud.providers.onedrive import OneDriveAdapter
from apps.common.exceptions import ProviderAuthException


@override_settings(
    ONEDRIVE_OAUTH_CLIENT_ID="test-client-id",
    ONEDRIVE_OAUTH_CLIENT_SECRET="test-client-secret",
    ONEDRIVE_OAUTH_REDIRECT_URI="http://testserver/api/cloud/providers/onedrive/callback/",
    ONEDRIVE_OAUTH_TENANT="common",
)
class OneDriveOAuthAdapterTests(TestCase):
    def setUp(self):
        self.adapter = OneDriveAdapter()

    def test_authorization_url_includes_scopes_and_state(self):
        url = self.adapter.get_authorization_url(
            state="state-123",
            redirect_uri="http://testserver/api/cloud/providers/onedrive/callback/",
        )

        self.assertIn("login.microsoftonline.com/common/oauth2/v2.0/authorize", url)
        self.assertIn("response_mode=query", url)
        self.assertIn("state=state-123", url)
        self.assertIn("offline_access", url)
        self.assertIn("Files.ReadWrite", url)

    @patch("apps.cloud.providers.onedrive.OneDriveAdapter.get_account_identity")
    @patch("apps.cloud.providers.onedrive.OneDriveAdapter.get_quota")
    @patch("apps.cloud.providers.onedrive.OneDriveAdapter._msal_app")
    def test_exchange_code_returns_credentials_identity_and_quota(
        self,
        mock_msal_app,
        mock_get_quota,
        mock_get_identity,
    ):
        mock_msal_app.return_value.acquire_token_by_authorization_code.return_value = {
            "access_token": "access-1",
            "refresh_token": "refresh-1",
            "expires_in": 3600,
            "scope": "User.Read Files.ReadWrite offline_access",
        }
        mock_get_identity.return_value = {
            "provider_account_id": "ms-1",
            "account_email": "user@example.com",
            "display_name_hint": "Test User",
        }
        mock_get_quota.return_value = {
            "quota_total_bytes": 1000,
            "quota_used_bytes": 100,
        }

        result = self.adapter.exchange_code(
            code="auth-code",
            redirect_uri="http://testserver/api/cloud/providers/onedrive/callback/",
        )

        self.assertEqual(result["credentials"]["access_token"], "access-1")
        self.assertEqual(result["credentials"]["refresh_token"], "refresh-1")
        self.assertIn("token_expiry", result["credentials"])
        self.assertEqual(result["identity"]["provider_account_id"], "ms-1")
        self.assertEqual(result["quota"]["quota_total_bytes"], 1000)

    @patch("apps.cloud.providers.onedrive.OneDriveAdapter._msal_app")
    def test_refresh_access_token_preserves_refresh_token(self, mock_msal_app):
        mock_msal_app.return_value.acquire_token_by_refresh_token.return_value = {
            "access_token": "access-2",
            "expires_in": 7200,
            "scope": "User.Read Files.ReadWrite",
        }

        payload = self.adapter.refresh_access_token(refresh_token="refresh-1")

        self.assertEqual(payload["access_token"], "access-2")
        self.assertEqual(payload["refresh_token"], "refresh-1")

    @patch("apps.cloud.providers.onedrive.OneDriveAdapter._msal_app")
    def test_exchange_code_maps_msal_error_to_provider_auth(self, mock_msal_app):
        mock_msal_app.return_value.acquire_token_by_authorization_code.return_value = {
            "error": "invalid_grant",
            "error_description": "Code expired",
        }

        with self.assertRaises(ProviderAuthException):
            self.adapter.exchange_code(
                code="bad-code",
                redirect_uri="http://testserver/api/cloud/providers/onedrive/callback/",
            )

    @patch("apps.cloud.providers.onedrive._graph_get")
    def test_get_account_identity_parses_graph_profile(self, mock_graph_get):
        mock_graph_get.return_value = {
            "id": "ms-account",
            "mail": "onedrive@example.com",
            "displayName": "OneDrive User",
        }

        identity = self.adapter.get_account_identity(
            credentials={"access_token": "token-1"}
        )

        self.assertEqual(identity["provider_account_id"], "ms-account")
        self.assertEqual(identity["account_email"], "onedrive@example.com")
        self.assertEqual(identity["display_name_hint"], "OneDrive User")

    @patch("apps.cloud.providers.onedrive._graph_get")
    def test_get_quota_parses_drive_quota(self, mock_graph_get):
        mock_graph_get.return_value = {
            "quota": {
                "total": 2048,
                "used": 512,
            }
        }

        quota = self.adapter.get_quota(credentials={"access_token": "token-1"})

        self.assertEqual(quota["quota_total_bytes"], 2048)
        self.assertEqual(quota["quota_used_bytes"], 512)
