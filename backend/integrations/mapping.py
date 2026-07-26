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
            "pnr": payload.get("pnr"),
            "ticket_number": payload.get("ticket_number"),
            "itinerary": payload.get("itinerary"),
            "voided": payload.get("voided", False),
        }
        for k, v in payload.items():
            if k not in normalized:
                normalized[k] = v
        return normalized


class ErrorMapper:
    @staticmethod
    def map_error(error: Exception) -> dict[str, Any]:
        return {"error_type": error.__class__.__name__, "message": str(error)}
