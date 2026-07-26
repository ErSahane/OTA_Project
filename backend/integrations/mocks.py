from __future__ import annotations

from typing import Any

from .adapters import BaseAdapter
from .models import ProviderConfiguration


class MockProvider(BaseAdapter):
    def __init__(self, config: ProviderConfiguration):
        super().__init__(config)
        self.name = config.provider_name or "mock-provider"

    def fetch_catalog(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"provider": self.name, "status": "ok", "data": [{"id": "mock-flight", "name": "Mock Flight", "price": 199.0}]}

    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"provider": self.name, "status": "ok", "booking_reference": "MOCK-1001", "payload": payload}

    def cancel_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"provider": self.name, "status": "ok", "cancelled": True, "payload": payload}

    def issue_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        import secrets
        digits = "".join(secrets.choice("0123456789") for _ in range(10))
        ticket_number = f"176{digits}"
        return {"provider": self.name, "status": "ok", "pnr": "PNR123", "ticket_number": ticket_number, "payload": payload}

    def sync_pnr(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"provider": self.name, "status": "ok", "pnr": payload.get("provider_pnr", "PNR123"), "itinerary": {"segments": [{"from": "LHR", "to": "JFK"}]}}

    def void_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"provider": self.name, "status": "ok", "voided": True, "payload": payload}
