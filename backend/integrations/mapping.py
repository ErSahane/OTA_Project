from __future__ import annotations

from typing import Any


class ResponseMapper:
    @staticmethod
    def map_response(provider_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "provider": provider_name,
            "status": payload.get("status", "unknown"),
            "data": payload.get("data", []),
            "booking_reference": payload.get("booking_reference"),
            "cancelled": payload.get("cancelled", False),
        }
        return normalized


class ErrorMapper:
    @staticmethod
    def map_error(error: Exception) -> dict[str, Any]:
        return {"error_type": error.__class__.__name__, "message": str(error)}
