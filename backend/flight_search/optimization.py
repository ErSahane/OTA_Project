"""Provider-neutral cached-result filtering, sorting, pagination, and analytics."""

import hashlib
import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.cache import cache

from integrations.metrics import metrics


class SearchAnalyticsHook:
    def record(self, event_name, payload):
        pass


analytics = SearchAnalyticsHook()


class SearchResultCache:
    namespace = "flight-search:v2"

    @classmethod
    def key_for(cls, payload):
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return f"{cls.namespace}:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"

    @classmethod
    def get(cls, payload):
        return cache.get(cls.key_for(payload))

    @classmethod
    def set(cls, payload, value):
        cache.set(cls.key_for(payload), value, timeout=getattr(settings, "FLIGHT_SEARCH_CACHE_TTL_SECONDS", 900))


class SearchResultProcessor:
    """Applies request-time presentation options to normalized supplier results."""

    @staticmethod
    def _number(value, default=None):
        if isinstance(value, dict):
            value = value.get("amount", value.get("total"))
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return default

    @classmethod
    def _price(cls, item):
        return cls._number(item.get("total_price", item.get("price")), Decimal("Infinity"))

    @staticmethod
    def _integer(item, field, default):
        try:
            return int(item.get(field, default))
        except (TypeError, ValueError):
            return default

    @classmethod
    def process(cls, results, options):
        options = options or {}
        providers = set(options.get("providers", []))
        airlines = set(options.get("airlines", []))
        min_price, max_price = options.get("min_price"), options.get("max_price")
        max_stops = options.get("max_stops")

        filtered = []
        for item in results:
            price = cls._price(item)
            airline = item.get("airline", item.get("validating_carrier"))
            if providers and item.get("provider") not in providers:
                continue
            if airlines and airline not in airlines:
                continue
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            if max_stops is not None and cls._integer(item, "stops", 0) > max_stops:
                continue
            filtered.append(item)

        sort = options.get("sort", "price")
        descending = sort.startswith("-")
        field = sort.lstrip("-")
        sort_key = {
            "price": cls._price,
            "duration": lambda item: cls._integer(item, "duration_minutes", 999999),
            "stops": lambda item: cls._integer(item, "stops", 999),
        }[field]
        ordered = sorted(filtered, key=lambda item: (sort_key(item), item.get("provider_priority", 999)), reverse=descending)
        page, page_size = options.get("page", 1), options.get("page_size", 20)
        start = (page - 1) * page_size
        return ordered[start:start + page_size], {"page": page, "page_size": page_size, "total_results": len(ordered), "total_pages": (len(ordered) + page_size - 1) // page_size}

    @staticmethod
    def record(cache_status, correlation_id, result_count):
        metrics.increment("flight_search.cache", tags={"status": cache_status})
        analytics.record("flight_search.completed", {"correlation_id": correlation_id, "cache_status": cache_status, "result_count": result_count})
