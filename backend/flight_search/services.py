import logging
import uuid

from integrations.aggregation import ProviderAggregationService
from .models import FlightSearchLog
from .optimization import SearchResultCache, SearchResultProcessor

logger = logging.getLogger(__name__)


class FlightSearchService:
    """Flight-search persistence plus reusable cache and result optimization."""

    @staticmethod
    def _payload(query):
        return {
            "trip_type": query.trip_type,
            "cabin_class": query.cabin_class,
            "passenger_adults": query.passenger_adults,
            "passenger_children": query.passenger_children,
            "passenger_infants": query.passenger_infants,
            "segments": [
                {"origin": segment.origin, "destination": segment.destination,
                 "departure_date": segment.departure_date.isoformat(),
                 "return_date": segment.return_date.isoformat() if segment.return_date else None}
                for segment in query.segments.order_by("sequence")
            ],
        }

    @classmethod
    def _response(cls, query, results, cached, correlation_id, options):
        page_results, pagination = SearchResultProcessor.process(results, options)
        SearchResultProcessor.record("hit" if cached else "miss", correlation_id, len(results))
        return {"search_id": str(query.id), "correlation_id": correlation_id, **cls._payload(query), "results": page_results, "pagination": pagination, "cached": cached}

    @classmethod
    def search(cls, query, correlation_id=None, options=None):
        correlation_id = correlation_id or str(uuid.uuid4())
        payload = cls._payload(query)
        cached_results = SearchResultCache.get(payload)
        if cached_results is not None:
            logger.info("Flight search cache hit", extra={"search_id": str(query.id), "correlation_id": correlation_id})
            return cls._response(query, cached_results, cached=True, correlation_id=correlation_id, options=options)

        aggregation = ProviderAggregationService().aggregate_flight_search(payload, correlation_id)
        for outcome in aggregation["provider_outcomes"]:
            FlightSearchLog.objects.create(
                query=query, provider_name=outcome["provider_name"], status=outcome["status"],
                response_time_ms=outcome["elapsed_ms"], results_count=len(outcome["results"]), error_message=outcome["error_message"],
            )
        SearchResultCache.set(payload, aggregation["results"])
        return cls._response(query, aggregation["results"], cached=False, correlation_id=aggregation["correlation_id"], options=options)
