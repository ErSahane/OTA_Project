from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from .aggregation import ProviderAggregationService
from .factory import ProviderFactory
from .mapping import ErrorMapper, ResponseMapper
from .models import ProviderConfiguration
from .services import ProviderService


class ProviderIntegrationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.config = ProviderConfiguration.objects.create(provider_name="mock-demo", provider_type="mock", priority=10, timeout_seconds=5, retry_count=1)

    def test_provider_factory_creates_provider(self):
        self.assertEqual(ProviderFactory.create_provider(self.config).name, "mock-demo")

    def test_service_fetch_catalog_returns_mapped_response(self):
        result = ProviderService(self.config).fetch_catalog({"source": "tests"})
        self.assertEqual(result["status"], "ok")
        self.assertIn("provider", result)

    def test_response_mapper_normalizes_payload(self):
        self.assertEqual(ResponseMapper.map_response("mock", {"status": "ok", "data": [{"id": 1}]})["provider"], "mock")
        self.assertEqual(ErrorMapper.map_error(ValueError("boom"))["message"], "boom")


class ProviderAggregationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.primary = ProviderConfiguration.objects.create(provider_name="primary", provider_type="mock", priority=1, retry_count=0)
        self.secondary = ProviderConfiguration.objects.create(provider_name="secondary", provider_type="mock", priority=20, retry_count=1)
        self.service = ProviderAggregationService()

    def test_aggregates_deduplicates_and_ranks_by_priority(self):
        def response(service, payload, **kwargs):
            return {"status": "ok", "data": [
                {"id": "same-flight", "price": 200},
                {"id": f"{service.config.provider_name}-cheap", "price": 100},
            ]}

        with patch.object(ProviderService, "fetch_catalog", autospec=True, side_effect=response):
            result = self.service.aggregate_flight_search({"segments": []}, "corr-1")

        self.assertEqual(result["correlation_id"], "corr-1")
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(result["results"][0]["price"], 100)
        same = next(item for item in result["results"] if item["id"] == "same-flight")
        self.assertEqual(same["provider"], "primary")

    def test_partial_failure_retries_without_losing_successes(self):
        calls = {"secondary": 0}

        def response(service, payload, **kwargs):
            if service.config.provider_name == "secondary":
                calls["secondary"] += 1
                raise RuntimeError("provider unavailable")
            return {"status": "ok", "data": [{"id": "available", "price": 150}]}

        with patch.object(ProviderService, "fetch_catalog", autospec=True, side_effect=response):
            result = self.service.aggregate_flight_search({"segments": []})

        self.assertEqual(len(result["results"]), 1)
        outcomes = {outcome["provider_name"]: outcome for outcome in result["provider_outcomes"]}
        self.assertEqual(outcomes["primary"]["status"], "success")
        self.assertEqual(outcomes["secondary"]["status"], "error")
        self.assertEqual(calls["secondary"], 2)

    def test_circuit_opens_after_repeated_failures(self):
        self.primary.retry_count = 0
        self.primary.save(update_fields=["retry_count"])
        self.secondary.enabled = False
        self.secondary.save(update_fields=["enabled"])
        with patch.object(ProviderService, "fetch_catalog", autospec=True, side_effect=RuntimeError("down")):
            for _ in range(3):
                self.service.aggregate_flight_search({"segments": []})
            result = self.service.aggregate_flight_search({"segments": []})
        self.assertEqual(result["provider_outcomes"][0]["status"], "circuit_open")
