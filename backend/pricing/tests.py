from django.test import TestCase
from rest_framework.test import APIClient

from .models import FarePolicy, PricingAdjustment
from .serializers import PricingQuoteSerializer
from .services import PricingEngine


class PricingEngineTests(TestCase):
    def setUp(self):
        FarePolicy.objects.create(
            code="FLEXI",
            fare_family="Flex",
            fare_basis="YFLEX",
            currency="USD",
            refundable=True,
            cancellation_allowed=True,
            date_change_allowed=True,
            cancellation_penalty="25.00",
            date_change_penalty="15.00",
            baggage_rules={"checked_bags": 1, "cabin_bags": 1},
            refund_rules={"window_hours": 24},
            ancillary_rules={"meal": True, "wifi": True},
        )
        PricingAdjustment.objects.create(code="MARKUP_STD", name="Standard markup", adjustment_type=PricingAdjustment.MARKUP, amount_type=PricingAdjustment.PERCENTAGE, amount="10.0000", currency="USD", priority=10)
        PricingAdjustment.objects.create(code="SERVICE_STD", name="Service fee", adjustment_type=PricingAdjustment.SERVICE_FEE, amount_type=PricingAdjustment.FIXED, amount="5.00", currency="USD", priority=20)
        PricingAdjustment.objects.create(code="DISC_MEMBER", name="Member discount", adjustment_type=PricingAdjustment.DISCOUNT, amount_type=PricingAdjustment.FIXED, amount="7.50", currency="USD", priority=30)
        PricingAdjustment.objects.create(code="PROMO10", name="Promo 10", adjustment_type=PricingAdjustment.PROMO, amount_type=PricingAdjustment.FIXED, amount="10.00", currency="USD", promo_code="SAVE10", priority=40)
        self.client = APIClient()

    def payload(self, **overrides):
        data = {
            "currency": "usd",
            "base_fare": "100.00",
            "passengers": [{"passenger_type": "ADT", "quantity": 2}],
            "taxes": [{"code": "XT", "name": "Airport tax", "amount": "12.50"}],
            "ancillaries": [{"code": "BAG", "name": "Extra bag", "amount": "20.00", "quantity": 1}],
            "seats": [{"code": "SEAT", "name": "Seat", "amount": "15.00", "quantity": 2}],
            "fare_policy_code": "FLEXI",
            "promo_code": "SAVE10",
        }
        data.update(overrides)
        return data

    def test_quote_serializer_validates_passenger_cap(self):
        serializer = PricingQuoteSerializer(data=self.payload(passengers=[{"passenger_type": "ADT", "quantity": 10}]))
        self.assertFalse(serializer.is_valid())

    def test_pricing_engine_builds_breakdown_and_rules(self):
        quote = PricingEngine.quote(PricingQuoteSerializer(data=self.payload()).run_validation(self.payload()))
        self.assertEqual(quote["currency"], "USD")
        self.assertEqual(quote["fare_rules"]["fare_family"], "Flex")
        self.assertEqual(quote["totals"]["base_fare"], "200.00")
        self.assertEqual(quote["totals"]["taxes"], "25.00")
        self.assertEqual(quote["totals"]["grand_total"], "285.00")

    def test_quote_without_policy_or_promo_still_prices(self):
        quote = PricingEngine.quote(PricingQuoteSerializer(data=self.payload(fare_policy_code="", promo_code="", ancillaries=[], seats=[])).run_validation(self.payload(fare_policy_code="", promo_code="", ancillaries=[], seats=[])))
        self.assertEqual(quote["fare_rules"]["fare_family"], None)
        self.assertEqual(quote["totals"]["discounts"], "7.50")

    def test_quote_endpoint(self):
        response = self.client.post('/api/v1/pricing/quote/', self.payload(), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["totals"]["grand_total"], "285.00")
        self.assertEqual(response.data["fare_rules"]["baggage"]["checked_bags"], 1)
