from __future__ import annotations

import logging
from typing import Any

from .interfaces import ProviderInterface
from .models import ProviderConfiguration

logger = logging.getLogger(__name__)


class BaseAdapter(ProviderInterface):
    def __init__(self, config: ProviderConfiguration):
        self.config = config
        self.name = config.provider_name

    def _build_context(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"provider": self.name, "payload": payload or {}}

    def fetch_catalog(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        logger.info("Fetching catalog", extra=self._build_context(payload))
        return {"provider": self.name, "status": "ok", "data": []}

    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("Creating booking", extra=self._build_context(payload))
        return {"provider": self.name, "status": "ok", "booking_reference": "mock-booking"}

    def cancel_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("Cancelling booking", extra=self._build_context(payload))
        return {"provider": self.name, "status": "ok", "cancelled": True}

    def issue_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("Issuing ticket", extra=self._build_context(payload))
        return {"provider": self.name, "status": "ok", "pnr": "MOCKPNR", "ticket_number": "1761234567890"}

    def sync_pnr(self, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("Synchronizing pnr", extra=self._build_context(payload))
        return {"provider": self.name, "status": "ok", "pnr": payload.get("provider_pnr", "MOCKPNR"), "itinerary": {"segments": payload.get("segments", [])}}

    def void_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("Voiding ticket", extra=self._build_context(payload))
        return {"provider": self.name, "status": "ok", "voided": True}
