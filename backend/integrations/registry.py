from __future__ import annotations

from typing import Any

from .mocks import MockProvider
from .models import ProviderConfiguration


class ProviderRegistry:
    _providers: dict[str, type] = {"mock": MockProvider}

    @classmethod
    def register(cls, name: str, provider_cls: type) -> None:
        cls._providers[name] = provider_cls

    @classmethod
    def get_provider_class(cls, provider_name: str) -> type:
        return cls._providers.get(provider_name, MockProvider)
