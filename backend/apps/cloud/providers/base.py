from abc import ABC, abstractmethod
from typing import Any

from apps.common.constants import ProviderType
from apps.common.exceptions import ProviderNotImplementedException


class CloudProviderAdapter(ABC):
    """
    Strategy/Adapter contract for cloud storage providers.

    Phase 1 registers stub adapters. Concrete OAuth and file I/O
    land in later phases without changing domain services.
    """

    provider_type: str

    @abstractmethod
    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        """Return the provider OAuth consent URL."""

    @abstractmethod
    def exchange_code(self, *, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange an authorization code for tokens and account identity."""

    @abstractmethod
    def refresh_access_token(self, *, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token."""

    @abstractmethod
    def revoke_credentials(self, *, credentials: dict[str, Any]) -> None:
        """Best-effort revoke of provider credentials on unlink."""

    @abstractmethod
    def get_account_identity(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        """Return provider account id, email, and display hints."""

    @abstractmethod
    def get_quota(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        """Return storage quota information for the connected account."""


class StubCloudProviderAdapter(CloudProviderAdapter):
    """Base stub that raises until a real adapter is implemented."""

    provider_type: str = ""

    def _not_implemented(self) -> None:
        label = (
            ProviderType(self.provider_type).label
            if self.provider_type in ProviderType.values
            else self.provider_type or "Unknown"
        )
        raise ProviderNotImplementedException(
            f"{label} provider integration is not implemented yet."
        )

    def get_authorization_url(self, *, state: str, redirect_uri: str) -> str:
        self._not_implemented()

    def exchange_code(self, *, code: str, redirect_uri: str) -> dict[str, Any]:
        self._not_implemented()

    def refresh_access_token(self, *, refresh_token: str) -> dict[str, Any]:
        self._not_implemented()

    def revoke_credentials(self, *, credentials: dict[str, Any]) -> None:
        self._not_implemented()

    def get_account_identity(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        self._not_implemented()

    def get_quota(self, *, credentials: dict[str, Any]) -> dict[str, Any]:
        self._not_implemented()
