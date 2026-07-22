from __future__ import annotations

from .models import ProviderConfiguration
from .registry import ProviderRegistry


class ProviderFactory:
    @staticmethod
    def create_provider(config: ProviderConfiguration):
        provider_cls = ProviderRegistry.get_provider_class(config.provider_type)
        return provider_cls(config)
