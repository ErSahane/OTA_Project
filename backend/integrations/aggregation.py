"""Generic parallel orchestration for catalog-search providers."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Any

from django.conf import settings

from .circuit_breaker import ProviderCircuitBreaker
from .metrics import metrics
from .models import ProviderConfiguration
from .services import ProviderService

logger = logging.getLogger(__name__)


@dataclass
class ProviderOutcome:
    provider_name: str
    status: str
    results: list[dict[str, Any]]
    elapsed_ms: int
    attempts: int
    error_message: str = ""


class UnifiedFlightMapper:
    """Normalizes common metadata without coupling to a supplier schema."""

    @staticmethod
    def map_result(item, provider_name, priority):
        if not isinstance(item, dict):
            return None
        result = dict(item)
        result["provider"] = provider_name
        result["provider_priority"] = priority
        return result

    @staticmethod
    def dedupe_key(item):
        itinerary = item.get("segments") or item.get("itinerary") or item.get("legs") or item.get("id")
        fare = item.get("total_price", item.get("price", {}))
        if isinstance(fare, dict):
            fare = {"amount": fare.get("amount", fare.get("total")), "currency": fare.get("currency")}
        canonical = json.dumps({"itinerary": itinerary, "fare": fare}, sort_keys=True, default=str, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class FlightRankingEngine:
    @staticmethod
    def _price(item):
        value = item.get("total_price", item.get("price", float("inf")))
        if isinstance(value, dict):
            value = value.get("amount", value.get("total", float("inf")))
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("inf")

    @classmethod
    def rank(cls, results):
        return sorted(results, key=lambda item: (cls._price(item), item.get("stops", 999), item.get("duration_minutes", 999999), item.get("provider_priority", 999)))


class ProviderAggregationService:
    """Runs enabled providers concurrently and returns successful partial results."""

    def __init__(self, metrics_hook=None):
        self.metrics = metrics_hook or metrics
        self.failure_threshold = getattr(settings, "PROVIDER_CIRCUIT_FAILURE_THRESHOLD", 3)
        self.recovery_timeout = getattr(settings, "PROVIDER_CIRCUIT_RECOVERY_SECONDS", 60)

    def aggregate_flight_search(self, payload, correlation_id=None):
        correlation_id = correlation_id or str(uuid.uuid4())
        providers = list(ProviderConfiguration.objects.filter(enabled=True).order_by("priority", "provider_name"))
        if not providers:
            return {"correlation_id": correlation_id, "results": [], "provider_outcomes": []}

        max_workers = min(len(providers), getattr(settings, "PROVIDER_AGGREGATION_MAX_WORKERS", 8))
        outcomes = []
        executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="provider-search")
        futures = {executor.submit(self._execute_provider, provider, payload, correlation_id): provider for provider in providers}
        try:
            deadline = max(provider.timeout_seconds for provider in providers)
            for future in as_completed(futures, timeout=deadline):
                provider = futures[future]
                try:
                    outcomes.append(future.result())
                except Exception as exc:  # defensive: _execute_provider is expected to contain errors
                    outcomes.append(ProviderOutcome(provider.provider_name, "error", [], 0, 1, str(exc)))
        except TimeoutError:
            logger.warning("Provider aggregation deadline exceeded", extra={"correlation_id": correlation_id})
        finally:
            for future, provider in futures.items():
                if not future.done():
                    future.cancel()
                    outcomes.append(ProviderOutcome(provider.provider_name, "timeout", [], provider.timeout_seconds * 1000, 1, "Provider aggregation timeout."))
            executor.shutdown(wait=False, cancel_futures=True)

        results = self._deduplicate_and_rank(outcomes)
        failed = sum(outcome.status != "success" for outcome in outcomes)
        self.metrics.increment("provider_aggregation.completed", tags={"correlation_id": correlation_id, "partial_failure": str(bool(failed)).lower()})
        logger.info("Provider aggregation completed", extra={"correlation_id": correlation_id, "provider_count": len(outcomes), "failed_provider_count": failed, "result_count": len(results)})
        return {"correlation_id": correlation_id, "results": results, "provider_outcomes": [asdict(outcome) for outcome in outcomes]}

    def _execute_provider(self, provider, payload, correlation_id):
        started = time.perf_counter()
        breaker = ProviderCircuitBreaker(provider.provider_name, self.failure_threshold, self.recovery_timeout)
        if not breaker.allow_request():
            self.metrics.increment("provider_aggregation.circuit_open", tags={"provider": provider.provider_name})
            return ProviderOutcome(provider.provider_name, "circuit_open", [], 0, 0, "Circuit breaker is open.")

        attempts = max(1, provider.retry_count + 1)
        last_error = ""
        for attempt in range(1, attempts + 1):
            try:
                response = ProviderService(provider).fetch_catalog({**payload, "correlation_id": correlation_id}, record_call=False)
                if response.get("status") == "ok" and isinstance(response.get("data", []), list):
                    results = [UnifiedFlightMapper.map_result(item, provider.provider_name, provider.priority) for item in response["data"]]
                    breaker.record_success()
                    elapsed_ms = int((time.perf_counter() - started) * 1000)
                    self.metrics.timing("provider_aggregation.provider_latency", elapsed_ms, tags={"provider": provider.provider_name, "status": "success"})
                    return ProviderOutcome(provider.provider_name, "success", [item for item in results if item], elapsed_ms, attempt)
                last_error = response.get("error", {}).get("message", "Provider returned an invalid search response.")
            except Exception as exc:
                last_error = str(exc)
            if attempt < attempts:
                time.sleep(min(0.1 * (2 ** (attempt - 1)), 1.0))

        breaker.record_failure()
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        self.metrics.increment("provider_aggregation.provider_failure", tags={"provider": provider.provider_name})
        self.metrics.timing("provider_aggregation.provider_latency", elapsed_ms, tags={"provider": provider.provider_name, "status": "error"})
        logger.warning("Provider search failed", extra={"provider": provider.provider_name, "correlation_id": correlation_id, "attempts": attempts, "error": last_error})
        return ProviderOutcome(provider.provider_name, "error", [], elapsed_ms, attempts, last_error)

    @staticmethod
    def _deduplicate_and_rank(outcomes):
        deduplicated = {}
        for outcome in outcomes:
            for item in outcome.results:
                key = UnifiedFlightMapper.dedupe_key(item)
                existing = deduplicated.get(key)
                if existing is None or item["provider_priority"] < existing["provider_priority"]:
                    deduplicated[key] = item
        return FlightRankingEngine.rank(list(deduplicated.values()))

