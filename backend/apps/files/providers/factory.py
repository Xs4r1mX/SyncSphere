from apps.common.constants import ProviderType
from apps.common.exceptions import InvalidProviderException, ProviderNotImplementedException

from .base import CloudFileAdapter


class FileProviderFactory:
    _registry: dict[str, type[CloudFileAdapter]] = {}

    @classmethod
    def register(cls, adapter_cls: type[CloudFileAdapter]) -> None:
        cls._registry[adapter_cls.provider_type] = adapter_cls

    @classmethod
    def get(cls, provider: str) -> CloudFileAdapter:
        if provider not in cls._registry:
            if provider in ProviderType.values:
                raise ProviderNotImplementedException()
            raise InvalidProviderException()

        return cls._registry[provider]()

    @classmethod
    def supported_providers(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()
