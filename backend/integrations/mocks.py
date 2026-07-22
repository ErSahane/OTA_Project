from __future__ import annotations

from typing import Any

from .adapters import BaseAdapter
from .models import ProviderConfiguration


class MockProvider(BaseAdapter):
    def __init__(self, config: ProviderConfiguration):
        super().__init__(config)
        self.name = config.provider_name or "mock-provider"

    def fetch_catalog(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "provider": self.name,
            "status": "ok",
            "data": [{"id": "mock-flight", "name": "Mock Flight", "price": 199.0}],
        }

    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.name,
            "status": "ok",
            "booking_reference": "MOCK-1001",
            "payload": payload,
        }

    def cancel_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "provider": self.name,
            "status": "ok",
            "cancelled": True,
            "payload": payload,
        }
