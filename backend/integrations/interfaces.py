from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderInterface(ABC):
    name: str = ""

    @abstractmethod
    def fetch_catalog(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def cancel_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
