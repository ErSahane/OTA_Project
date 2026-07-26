from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from datetime import date

from integrations.models import ProviderConfiguration
from pricing.models import FarePolicy, PricingAdjustment

from .models import Booking, BookingAuditEvent, BookingSession
from .serializers import BookingSessionCreateSerializer
from .services import BookingService


User = get_user_model()


class BookingFoundationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="traveler@example.com", username="traveler", password="pass12345")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        ProviderConfiguration.objects.create(provider_name="mock-provider", provider_type="mock")
        FarePolicy.objects.create(code="FLEXI", fare_family="Flex", fare_basis="YFLEX", currency="USD", refundable=True, cancellation_allowed=True, date_change_allowed=True, cancellation_penalty="20.00", date_change_penalty="10.00", baggage_rules={"checked_bags": 1}, refund_rules={"window_hours": 24}, ancillary_rules={"meal": True})
        PricingAdjustment.objects.create(code="MARKUP_STD", name="Markup", adjustment_type=PricingAdjustment.MARKUP, amount_type=PricingAdjustment.PERCENTAGE, amount="10.0000", currency="USD")

    def payload(self, **overrides):
        data = {
            "provider_name": "mock-provider",
            "search_reference": "search-123",
            "selected_offer": {"offer_id": "offer-1", "seat_available": True},
            "pricing_request": {"currency": "USD", "base_fare": "100.00", "passengers": [{"passenger_type": "ADT", "quantity": 1}], "taxes": [], "ancillaries": [], "seats": [], "fare_policy_code": "FLEXI", "promo_code": ""},
            "passengers": [{"passenger_type": "ADT", "title": "Mr", "first_name": "John", "last_name": "Doe", "gender": "M", "date_of_birth": "1990-01-01", "ssr_codes": ["VGML"]}],
            "contact": {"first_name": "John", "last_name": "Doe", "email": "john@example.com", "phone": "+123456789"},
            "hold_minutes": 15,
            "idempotency_key": "idem-booking-1",
        }
        data.update(overrides)
        return data

    def test_session_serializer_validates_infant_ratio(self):
        serializer = BookingSessionCreateSerializer(data=self.payload(passengers=[{"passenger_type": "INF", "first_name": "Inf", "last_name": "Doe", "date_of_birth": "2025-01-01"}]))
        self.assertFalse(serializer.is_valid())

    def test_create_session_is_idempotent_and_audited(self):
        serializer = BookingSessionCreateSerializer(data=self.payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        first = BookingService.create_session(serializer.validated_data, user=self.user, correlation_id="corr-1")
        second = BookingService.create_session(serializer.validated_data, user=self.user, correlation_id="corr-1")
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.status, BookingSession.STATUS_HELD)
        self.assertGreaterEqual(BookingAuditEvent.objects.filter(session=first).count(), 2)

    def test_seat_validation_blocks_unavailable_offer(self):
        serializer = BookingSessionCreateSerializer(data=self.payload(selected_offer={"offer_id": "offer-1", "seat_available": False}))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaisesMessage(Exception, "Selected offer no longer has seats available."):
            BookingService.create_session(serializer.validated_data, user=self.user)

    def test_confirm_booking_creates_reservation_and_reference(self):
        serializer = BookingSessionCreateSerializer(data=self.payload())
        serializer.is_valid(raise_exception=True)
        session = BookingService.create_session(serializer.validated_data, user=self.user, correlation_id="corr-2")
        booking = BookingService.confirm_booking(session.session_token, user=self.user)
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
        self.assertTrue(booking.reference.startswith("BKG"))
        self.assertEqual(booking.passengers.count(), 1)
        self.assertEqual(session.booking.reference, booking.reference)

    def test_confirm_booking_uses_locking(self):
        serializer = BookingSessionCreateSerializer(data=self.payload())
        serializer.is_valid(raise_exception=True)
        session = BookingService.create_session(serializer.validated_data, user=self.user)
        with patch("booking.services.cache.add", return_value=False):
            with self.assertRaisesMessage(Exception, "Booking request is already being processed."):
                BookingService.confirm_booking(session.session_token, user=self.user)

    def test_booking_api_flow(self):
        session_response = self.client.post("/api/v1/bookings/sessions/", self.payload(), format="json")
        self.assertEqual(session_response.status_code, 200)
        confirm_response = self.client.post("/api/v1/bookings/confirm/", {"session_token": session_response.data["session_token"]}, format="json")
        self.assertEqual(confirm_response.status_code, 200)
        booking_reference = confirm_response.data["reference"]
        detail_response = self.client.get(f"/api/v1/bookings/{booking_reference}/")
        status_response = self.client.get(f"/api/v1/bookings/{booking_reference}/status/")
        list_response = self.client.get("/api/v1/bookings/")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(status_response.data["status"], Booking.STATUS_CONFIRMED)
        self.assertEqual(len(list_response.data), 1)
