from django.test import TestCase

from .factory import ProviderFactory
from .mapping import ErrorMapper, ResponseMapper
from .models import ProviderConfiguration
from .services import ProviderService


class ProviderIntegrationTests(TestCase):
    def setUp(self):
        self.config = ProviderConfiguration.objects.create(
            provider_name="mock-demo",
            provider_type="mock",
            timeout_seconds=5,
            retry_count=2,
        )

    def test_provider_factory_creates_provider(self):
        provider = ProviderFactory.create_provider(self.config)
        self.assertEqual(provider.name, "mock-demo")

    def test_service_fetch_catalog_returns_mapped_response(self):
        service = ProviderService(self.config)
        result = service.fetch_catalog({"source": "tests"})
        self.assertEqual(result["status"], "ok")
        self.assertIn("provider", result)

    def test_response_mapper_normalizes_payload(self):
        payload = {"status": "ok", "data": [{"id": 1}]}
        mapped = ResponseMapper.map_response("mock", payload)
        self.assertEqual(mapped["provider"], "mock")
        self.assertEqual(mapped["data"], payload["data"])

    def test_error_mapper_formats_exception(self):
        mapped = ErrorMapper.map_error(ValueError("boom"))
        self.assertEqual(mapped["message"], "boom")
