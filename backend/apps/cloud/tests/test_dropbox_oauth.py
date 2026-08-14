from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.cloud.providers.dropbox import DropboxAdapter
from apps.common.exceptions import ProviderAuthException


@override_settings(
    DROPBOX_OAUTH_APP_KEY="test-app-key",
    DROPBOX_OAUTH_APP_SECRET="test-app-secret",
    DROPBOX_OAUTH_REDIRECT_URI="http://testserver/api/cloud/providers/dropbox/callback/",
)
class DropboxOAuthAdapterTests(TestCase):
    def setUp(self):
        self.adapter = DropboxAdapter()

    def test_authorization_url_includes_offline_access_and_scopes(self):
        url = self.adapter.get_authorization_url(
            state="state-123",
            redirect_uri="http://testserver/api/cloud/providers/dropbox/callback/",
        )

        self.assertIn("dropbox.com/oauth2/authorize", url)
        self.assertIn("token_access_type=offline", url)
        self.assertIn("state=state-123", url)
        self.assertIn("account_info.read", url)
        self.assertIn("files.content.write", url)

    @patch("apps.cloud.providers.dropbox.DropboxAdapter.get_account_identity")
    @patch("apps.cloud.providers.dropbox.DropboxAdapter.get_quota")
    @patch("apps.cloud.providers.dropbox._post_token")
    def test_exchange_code_returns_credentials_identity_and_quota(
        self,
        mock_post_token,
        mock_get_quota,
        mock_get_identity,
    ):
        mock_post_token.return_value = {
            "access_token": "access-1",
            "refresh_token": "refresh-1",
            "expires_in": 3600,
            "scope": "account_info.read files.content.read",
        }
        mock_get_identity.return_value = {
            "provider_account_id": "dbx-1",
            "account_email": "user@example.com",
            "display_name_hint": "Test User",
        }
        mock_get_quota.return_value = {
            "quota_total_bytes": 1000,
            "quota_used_bytes": 100,
        }

        result = self.adapter.exchange_code(
            code="auth-code",
            redirect_uri="http://testserver/api/cloud/providers/dropbox/callback/",
        )

        self.assertEqual(result["credentials"]["access_token"], "access-1")
        self.assertEqual(result["credentials"]["refresh_token"], "refresh-1")
        self.assertIn("token_expiry", result["credentials"])
        self.assertEqual(result["identity"]["provider_account_id"], "dbx-1")
        self.assertEqual(result["quota"]["quota_total_bytes"], 1000)

    @patch("apps.cloud.providers.dropbox._post_token")
    def test_refresh_access_token_preserves_refresh_token(self, mock_post_token):
        mock_post_token.return_value = {
            "access_token": "access-2",
            "expires_in": 7200,
            "scope": "account_info.read",
        }

        payload = self.adapter.refresh_access_token(refresh_token="refresh-1")

        self.assertEqual(payload["access_token"], "access-2")
        self.assertEqual(payload["refresh_token"], "refresh-1")

    @patch("apps.cloud.providers.dropbox._post_token")
    def test_exchange_code_maps_http_error_to_provider_auth(self, mock_post_token):
        import urllib.error

        mock_post_token.side_effect = urllib.error.HTTPError(
            url="https://api.dropbox.com/oauth2/token",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=None,
        )

        with self.assertRaises(ProviderAuthException):
            self.adapter.exchange_code(
                code="bad-code",
                redirect_uri="http://testserver/api/cloud/providers/dropbox/callback/",
            )

    @patch("apps.cloud.providers.dropbox.dropbox.Dropbox")
    def test_get_account_identity_parses_dropbox_account(self, mock_dropbox_cls):
        account = MagicMock()
        account.account_id = "dbx-account"
        account.email = "dropbox@example.com"
        account.name.display_name = "Dropbox User"
        mock_dropbox_cls.return_value.users_get_current_account.return_value = account

        identity = self.adapter.get_account_identity(
            credentials={"access_token": "token-1"}
        )

        self.assertEqual(identity["provider_account_id"], "dbx-account")
        self.assertEqual(identity["account_email"], "dropbox@example.com")
        self.assertEqual(identity["display_name_hint"], "Dropbox User")

    @patch("apps.cloud.providers.dropbox.dropbox.Dropbox")
    def test_get_quota_parses_space_usage(self, mock_dropbox_cls):
        from dropbox.users import IndividualSpaceAllocation, SpaceAllocation, SpaceUsage

        usage = SpaceUsage(
            used=512,
            allocation=SpaceAllocation.individual(
                IndividualSpaceAllocation(allocated=2048)
            ),
        )
        mock_dropbox_cls.return_value.users_get_space_usage.return_value = usage

        quota = self.adapter.get_quota(credentials={"access_token": "token-1"})

        self.assertEqual(quota["quota_total_bytes"], 2048)
        self.assertEqual(quota["quota_used_bytes"], 512)
