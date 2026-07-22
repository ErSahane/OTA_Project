import hashlib
import json
import logging
import time
from django.core.cache import cache

from integrations.models import ProviderConfiguration
from integrations.services import ProviderService
from .models import FlightSearchLog

logger = logging.getLogger(__name__)


class FlightSearchService:
    @staticmethod
    def _generate_cache_key(query) -> str:
        # Build a unique representation of the search parameters
        parts = [
            query.trip_type,
            query.cabin_class,
            str(query.passenger_adults),
            str(query.passenger_children),
            str(query.passenger_infants),
        ]
        # Append segments details sorted by sequence
        for seg in query.segments.all().order_by("sequence"):
            parts.append(
                f"{seg.origin}-{seg.destination}-{seg.departure_date}-"
                f"{seg.return_date if seg.return_date else ''}"
            )
        raw_key = ":".join(parts)
        hashed_key = hashlib.md5(raw_key.encode("utf-8")).hexdigest()
        return f"flight_search_cache:{hashed_key}"

    @classmethod
    def search(cls, query) -> dict:
        cache_key = cls._generate_cache_key(query)
        cached_results = cache.get(cache_key)

        if cached_results is not None:
            logger.info("Serving flight search results from cache", extra={"search_id": str(query.id)})
            return {
                "search_id": str(query.id),
                "trip_type": query.trip_type,
                "cabin_class": query.cabin_class,
                "passenger_adults": query.passenger_adults,
                "passenger_children": query.passenger_children,
                "passenger_infants": query.passenger_infants,
                "segments": [
                    {
                        "origin": seg.origin,
                        "destination": seg.destination,
                        "departure_date": seg.departure_date.isoformat(),
                        "return_date": seg.return_date.isoformat() if seg.return_date else None,
                    }
                    for seg in query.segments.all()
                ],
                "results": cached_results,
                "cached": True,
            }

        # Build payload for providers
        provider_payload = {
            "trip_type": query.trip_type,
            "cabin_class": query.cabin_class,
            "passenger_adults": query.passenger_adults,
            "passenger_children": query.passenger_children,
            "passenger_infants": query.passenger_infants,
            "segments": [
                {
                    "origin": seg.origin,
                    "destination": seg.destination,
                    "departure_date": seg.departure_date.isoformat(),
                    "return_date": seg.return_date.isoformat() if seg.return_date else None,
                }
                for seg in query.segments.all()
            ],
        }

        # Retrieve enabled providers
        enabled_configs = ProviderConfiguration.objects.filter(enabled=True)
        aggregated_results = []

        for config in enabled_configs:
            start_time = time.perf_counter()
            results_count = 0
            status_str = "success"
            err_msg = None

            try:
                service = ProviderService(config)
                # Query provider catalog
                response = service.fetch_catalog(provider_payload)
                if response.get("status") == "ok":
                    data = response.get("data", [])
                    results_count = len(data)
                    # Add supplier metadata to the itineraries
                    for item in data:
                        item["provider"] = config.provider_name
                    aggregated_results.extend(data)
                else:
                    status_str = "error"
                    err_msg = response.get("error", {}).get("message", "Provider returned error status")
            except Exception as e:
                status_str = "error"
                err_msg = str(e)
                logger.exception("Failed to query provider for flight search", extra={"provider": config.provider_name})

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Log provider query details
            FlightSearchLog.objects.create(
                query=query,
                provider_name=config.provider_name,
                status=status_str,
                response_time_ms=duration_ms,
                results_count=results_count,
                error_message=err_msg,
            )

        # Cache results for 15 minutes (900 seconds)
        cache.set(cache_key, aggregated_results, timeout=900)

        return {
            "search_id": str(query.id),
            "trip_type": query.trip_type,
            "cabin_class": query.cabin_class,
            "passenger_adults": query.passenger_adults,
            "passenger_children": query.passenger_children,
            "passenger_infants": query.passenger_infants,
            "segments": [
                {
                    "origin": seg.origin,
                    "destination": seg.destination,
                    "departure_date": seg.departure_date.isoformat(),
                    "return_date": seg.return_date.isoformat() if seg.return_date else None,
                }
                for seg in query.segments.all()
            ],
            "results": aggregated_results,
            "cached": False,
        }
