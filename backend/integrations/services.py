from __future__ import annotations

import logging
from typing import Any

from .factory import ProviderFactory
from .mapping import ErrorMapper, ResponseMapper
from .models import ProviderCallLog, ProviderConfiguration

logger = logging.getLogger(__name__)


class ProviderService:
    def __init__(self, config: ProviderConfiguration):
        self.config = config
        self.provider = ProviderFactory.create_provider(config)

    def fetch_catalog(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._execute("fetch_catalog", lambda: self.provider.fetch_catalog(payload))

    def create_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._execute("create_booking", lambda: self.provider.create_booking(payload))

    def cancel_booking(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._execute("cancel_booking", lambda: self.provider.cancel_booking(payload))

    def _execute(self, operation: str, action) -> dict[str, Any]:
        try:
            result = action()
            ProviderCallLog.objects.create(
                provider_name=self.config.provider_name,
                operation=operation,
                status="success",
                response_code="200",
                details="Provider call successful",
            )
            return ResponseMapper.map_response(self.config.provider_name, result)
        except Exception as exc:  # pragma: no cover - defensive path
            logger.exception("Provider call failed", extra={"provider": self.config.provider_name, "operation": operation})
            ProviderCallLog.objects.create(
                provider_name=self.config.provider_name,
                operation=operation,
                status="error",
                response_code="500",
                details=str(exc),
            )
            return {"status": "error", "provider": self.config.provider_name, "error": ErrorMapper.map_error(exc)}
