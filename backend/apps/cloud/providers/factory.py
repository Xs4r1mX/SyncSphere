from apps.common.constants import ProviderType
from apps.common.exceptions import InvalidProviderException, ProviderNotImplementedException

from .base import CloudProviderAdapter


class ProviderFactory:
    """
    Resolves provider adapters by ProviderType.

    Adapters register themselves from AppConfig.ready().
    """

    _registry: dict[str, type[CloudProviderAdapter]] = {}

    @classmethod
    def register(cls, adapter_cls: type[CloudProviderAdapter]) -> None:
        provider_type = getattr(adapter_cls, "provider_type", None)
        if not provider_type:
            raise ValueError("Adapter must define provider_type.")
        cls._registry[provider_type] = adapter_cls

    @classmethod
    def get(cls, provider: str) -> CloudProviderAdapter:
        if provider not in ProviderType.values:
            raise InvalidProviderException()

        adapter_cls = cls._registry.get(provider)
        if adapter_cls is None:
            raise ProviderNotImplementedException(
                f"No adapter registered for provider '{provider}'."
            )

        return adapter_cls()

    @classmethod
    def supported_providers(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        """Test helper to reset registrations."""
        cls._registry = {}
