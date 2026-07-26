from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from booking.models import Booking, BookingPassenger, BookingSession
from integrations.models import ProviderConfiguration
from pricing.models import FarePolicy, PricingAdjustment
from ticketing.models import Ticket
from ticketing.services import TicketingService

from .models import (
    CancellationAuditEvent,
    CancellationRequest,
    RefundClaim,
    RefundLedgerEntry,
)
from .services import (
    CancellationWorkflow,
    RefundCalculationEngine,
    RefundEligibilityEngine,
)

User = get_user_model()


class CancellationTestBase(TestCase):
    """Shared setUp for all cancellation tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="traveler@example.com",
            username="traveler",
            password="pass12345",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        ProviderConfiguration.objects.create(
            provider_name="mock-provider", provider_type="mock"
        )

        self.fare_policy = FarePolicy.objects.create(
            code="FLEXI",
            fare_family="Flex",
            fare_basis="YFLEX",
            currency="USD",
            refundable=True,
            cancellation_allowed=True,
            date_change_allowed=True,
            cancellation_penalty=Decimal("20.00"),
            date_change_penalty=Decimal("10.00"),
            baggage_rules={"checked_bags": 1},
            refund_rules={"window_hours": 24},
            ancillary_rules={"meal": True},
        )
        PricingAdjustment.objects.create(
            code="MARKUP_STD",
            name="Markup",
            adjustment_type=PricingAdjustment.MARKUP,
            amount_type=PricingAdjustment.PERCENTAGE,
            amount="10.0000",
            currency="USD",
        )

        self.session = BookingSession.objects.create(
            user=self.user,
            session_token="sess-cancel-1",
            booking_token="btoken-cancel-1",
            idempotency_key="idem-cancel-1",
            provider_name="mock-provider",
            quoted_total=Decimal("200.00"),
            currency="USD",
            contact_email="traveler@example.com",
            contact_phone="+12345678",
            contact_first_name="Jane",
            contact_last_name="Doe",
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
            pricing_request={
                "currency": "USD",
                "base_fare": "200.00",
                "fare_policy_code": "FLEXI",
                "passengers": [{"passenger_type": "ADT", "quantity": 2}],
                "taxes": [],
                "ancillaries": [],
                "seats": [],
                "promo_code": "",
            },
        )

        self.booking = Booking.objects.create(
            session=self.session,
            user=self.user,
            reference="BKGCANCEL001",
            provider_name="mock-provider",
            provider_booking_reference="GDSCNL001",
            currency="USD",
            total_amount=Decimal("200.00"),
            status=Booking.STATUS_CONFIRMED,
            contact_email="traveler@example.com",
            contact_phone="+12345678",
            contact_first_name="Jane",
            contact_last_name="Doe",
        )

        self.pax1 = BookingPassenger.objects.create(
            booking=self.booking,
            passenger_type="ADT",
            title="Ms",
            first_name="Jane",
            last_name="Doe",
            gender="F",
            date_of_birth=date(1990, 1, 1),
        )
        self.pax2 = BookingPassenger.objects.create(
            booking=self.booking,
            passenger_type="ADT",
            title="Mr",
            first_name="John",
            last_name="Doe",
            gender="M",
            date_of_birth=date(1988, 5, 10),
        )


# ---------------------------------------------------------------------------
# Unit Tests – Eligibility Engine
# ---------------------------------------------------------------------------

class RefundEligibilityEngineTests(CancellationTestBase):

    def test_eligible_with_valid_fare_policy(self):
        result = RefundEligibilityEngine.evaluate(self.booking)
        self.assertTrue(result["eligible"])
        self.assertTrue(result["refundable"])
        self.assertEqual(result["airline_penalty"], Decimal("20.00"))

    def test_non_refundable_policy_blocks_eligibility(self):
        self.fare_policy.cancellation_allowed = False
        self.fare_policy.save()
        result = RefundEligibilityEngine.evaluate(self.booking)
        self.assertFalse(result["eligible"])
        self.assertIn("does not permit cancellation", result["reason"])

    def test_no_policy_code_returns_ineligible(self):
        self.session.pricing_request = {}
        self.session.save()
        result = RefundEligibilityEngine.evaluate(self.booking)
        self.assertFalse(result["eligible"])


# ---------------------------------------------------------------------------
# Unit Tests – Calculation Engine
# ---------------------------------------------------------------------------

class RefundCalculationEngineTests(CancellationTestBase):

    def test_full_cancellation_calculation(self):
        result = RefundCalculationEngine.calculate(
            booking=self.booking,
            airline_penalty=Decimal("20.00"),
        )
        # gross=200, penalty=20, ota_fee=10, net=170
        self.assertEqual(result["gross_fare"], Decimal("200.00"))
        self.assertEqual(result["airline_penalty"], Decimal("20.00"))
        self.assertEqual(result["ota_fee"], Decimal("10.00"))
        self.assertEqual(result["net_refund"], Decimal("170.00"))

    def test_partial_passenger_cancellation_pro_rates(self):
        # Cancel 1 of 2 passengers
        result = RefundCalculationEngine.calculate(
            booking=self.booking,
            airline_penalty=Decimal("20.00"),
            cancelled_passenger_count=1,
            total_passenger_count=2,
        )
        # gross = 200 * 0.5 = 100, penalty = 20 * 0.5 = 10, ota_fee=10, net=80
        self.assertEqual(result["gross_fare"], Decimal("100.00"))
        self.assertEqual(result["airline_penalty"], Decimal("10.00"))
        self.assertEqual(result["net_refund"], Decimal("80.00"))

    def test_net_refund_floor_at_zero(self):
        # Penalty so high that net would go negative
        result = RefundCalculationEngine.calculate(
            booking=self.booking,
            airline_penalty=Decimal("300.00"),
        )
        self.assertEqual(result["net_refund"], Decimal("0.00"))


# ---------------------------------------------------------------------------
# Unit Tests – CancellationWorkflow
# ---------------------------------------------------------------------------

class CancellationWorkflowTests(CancellationTestBase):

    def test_full_booking_cancellation(self):
        # Issue tickets first so void can be tested
        TicketingService.issue_tickets(self.booking, "idem-issue-cancel", user=self.user)

        result = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-full-cancel",
            user=self.user,
        )
        cr = result["cancellation_request"]
        self.assertEqual(cr.status, CancellationRequest.STATUS_PENDING)
        self.assertEqual(cr.cancellation_type, CancellationRequest.TYPE_FULL)

        refund_claim = CancellationWorkflow.process_cancellation(cr, user=self.user)

        self.assertEqual(refund_claim.status, RefundClaim.STATUS_PENDING)
        self.assertEqual(refund_claim.gross_fare, Decimal("200.00"))
        self.assertEqual(refund_claim.airline_penalty, Decimal("20.00"))
        self.assertEqual(refund_claim.net_refund, Decimal("170.00"))

        # Booking should be cancelled
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.STATUS_CANCELLED)

        # Tickets should be voided
        for ticket in Ticket.objects.filter(booking=self.booking):
            self.assertEqual(ticket.status, Ticket.STATUS_VOIDED)

        # Ledger entries posted
        self.assertEqual(refund_claim.ledger_entries.count(), 4)
        credit = refund_claim.ledger_entries.get(entry_type=RefundLedgerEntry.TYPE_AIRLINE_CREDIT)
        payout = refund_claim.ledger_entries.get(entry_type=RefundLedgerEntry.TYPE_CUSTOMER_PAYOUT)
        self.assertEqual(credit.amount, Decimal("200.00"))
        self.assertEqual(payout.amount, Decimal("170.00"))

        # Audit trail
        self.assertTrue(CancellationAuditEvent.objects.filter(
            cancellation_request=cr, action="cancellation.approved"
        ).exists())

    def test_passenger_wise_cancellation(self):
        TicketingService.issue_tickets(self.booking, "idem-issue-paxcancel", user=self.user)

        result = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_PARTIAL_PASSENGERS,
            idempotency_key="idem-pax-cancel",
            passenger_ids=[str(self.pax1.id)],
            user=self.user,
        )
        cr = result["cancellation_request"]
        refund_claim = CancellationWorkflow.process_cancellation(cr, user=self.user)

        # Only 1 of 2 passengers → booking NOT fully cancelled
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.status, Booking.STATUS_CANCELLED)

        # Pro-rated gross fare: 200 * 1/2 = 100
        self.assertEqual(refund_claim.gross_fare, Decimal("100.00"))
        # Only pax1's ticket voided
        voided = Ticket.objects.filter(booking=self.booking, status=Ticket.STATUS_VOIDED)
        self.assertEqual(voided.count(), 1)
        self.assertEqual(voided.first().passenger, self.pax1)

    def test_idempotent_initiation(self):
        result1 = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-dup-cancel",
            user=self.user,
        )
        result2 = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-dup-cancel",
            user=self.user,
        )
        self.assertEqual(result1["cancellation_request"].id, result2["cancellation_request"].id)
        self.assertEqual(CancellationRequest.objects.filter(idempotency_key="idem-dup-cancel").count(), 1)

    def test_idempotent_approval(self):
        TicketingService.issue_tickets(self.booking, "idem-issue-idem", user=self.user)

        result = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-idem-cancel",
            user=self.user,
        )
        cr = result["cancellation_request"]
        claim1 = CancellationWorkflow.process_cancellation(cr, user=self.user)
        claim2 = CancellationWorkflow.process_cancellation(cr, user=self.user)
        self.assertEqual(claim1.id, claim2.id)

    def test_non_refundable_policy_blocks_initiation(self):
        self.fare_policy.cancellation_allowed = False
        self.fare_policy.save()

        with self.assertRaises(ValidationError):
            CancellationWorkflow.initiate_cancellation(
                booking=self.booking,
                cancellation_type=CancellationRequest.TYPE_FULL,
                idempotency_key="idem-nonref",
                user=self.user,
            )

    def test_rejection(self):
        result = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-reject-cancel",
            user=self.user,
        )
        cr = result["cancellation_request"]
        rejected = CancellationWorkflow.reject_cancellation(cr, rejection_reason="Test rejection", user=self.user)
        self.assertEqual(rejected.status, CancellationRequest.STATUS_REJECTED)
        self.assertEqual(rejected.rejection_reason, "Test rejection")

    def test_ledger_consistency(self):
        TicketingService.issue_tickets(self.booking, "idem-issue-ledger", user=self.user)

        result = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-ledger-cancel",
            user=self.user,
        )
        refund_claim = CancellationWorkflow.process_cancellation(result["cancellation_request"], user=self.user)

        # Sum of credits - Sum of debits should equal net refund
        credit_types = {RefundLedgerEntry.TYPE_AIRLINE_CREDIT, RefundLedgerEntry.TYPE_CUSTOMER_PAYOUT}
        debit_types = {RefundLedgerEntry.TYPE_PENALTY, RefundLedgerEntry.TYPE_OTA_FEE}
        credits = sum(e.amount for e in refund_claim.ledger_entries.filter(entry_type__in=credit_types))
        debits = sum(abs(e.amount) for e in refund_claim.ledger_entries.filter(entry_type__in=debit_types))
        self.assertEqual(credits - debits, refund_claim.net_refund)

    def test_refund_settlement(self):
        TicketingService.issue_tickets(self.booking, "idem-issue-settle", user=self.user)
        result = CancellationWorkflow.initiate_cancellation(
            booking=self.booking,
            cancellation_type=CancellationRequest.TYPE_FULL,
            idempotency_key="idem-settle-cancel",
            user=self.user,
        )
        refund_claim = CancellationWorkflow.process_cancellation(result["cancellation_request"], user=self.user)
        settled = CancellationWorkflow.settle_refund(refund_claim, gateway_reference="GW-TEST-001", user=self.user)

        self.assertEqual(settled.status, RefundClaim.STATUS_SETTLED)
        self.assertEqual(settled.gateway_reference, "GW-TEST-001")
        self.assertIsNotNone(settled.settled_at)


# ---------------------------------------------------------------------------
# Integration Tests – REST API
# ---------------------------------------------------------------------------

class CancellationAPITests(CancellationTestBase):

    def _issue_tickets(self):
        TicketingService.issue_tickets(self.booking, "idem-issue-api", user=self.user)

    def test_api_full_cancellation_flow(self):
        self._issue_tickets()

        # 1. Initiate
        payload = {
            "booking_reference": self.booking.reference,
            "cancellation_type": CancellationRequest.TYPE_FULL,
            "idempotency_key": "api-idem-full-cancel",
            "reason": "Change of plans",
        }
        resp = self.client.post("/api/v1/cancellations/requests/initiate/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        cr_id = resp.data["cancellation_request"]["id"]
        self.assertIn("estimate", resp.data)
        self.assertEqual(resp.data["estimate"]["net_refund"], "170.00")

        # 2. Approve
        resp2 = self.client.post(f"/api/v1/cancellations/requests/{cr_id}/approve/")
        self.assertEqual(resp2.status_code, 200, resp2.data)
        self.assertEqual(resp2.data["status"], RefundClaim.STATUS_PENDING)
        claim_id = resp2.data["id"]

        # 3. Retrieve refund claim
        resp3 = self.client.get(f"/api/v1/cancellations/refunds/{claim_id}/")
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(len(resp3.data["ledger_entries"]), 4)

        # 4. Settle
        resp4 = self.client.post(f"/api/v1/cancellations/refunds/{claim_id}/settle/")
        self.assertEqual(resp4.status_code, 200)
        self.assertEqual(resp4.data["status"], RefundClaim.STATUS_SETTLED)

    def test_api_partial_passenger_cancellation(self):
        self._issue_tickets()

        payload = {
            "booking_reference": self.booking.reference,
            "cancellation_type": CancellationRequest.TYPE_PARTIAL_PASSENGERS,
            "idempotency_key": "api-idem-pax-cancel",
            "passenger_ids": [str(self.pax1.id)],
        }
        resp = self.client.post("/api/v1/cancellations/requests/initiate/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        # Pro-rated: gross=100, net=80
        self.assertEqual(resp.data["estimate"]["gross_fare"], "100.00")
        self.assertEqual(resp.data["estimate"]["net_refund"], "80.00")

    def test_api_reject_cancellation(self):
        payload = {
            "booking_reference": self.booking.reference,
            "cancellation_type": CancellationRequest.TYPE_FULL,
            "idempotency_key": "api-idem-reject",
        }
        resp = self.client.post("/api/v1/cancellations/requests/initiate/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        cr_id = resp.data["cancellation_request"]["id"]

        resp2 = self.client.post(
            f"/api/v1/cancellations/requests/{cr_id}/reject/",
            {"rejection_reason": "Fraud suspected"},
            format="json",
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.data["status"], CancellationRequest.STATUS_REJECTED)

    def test_api_list_requests(self):
        self._issue_tickets()
        payload = {
            "booking_reference": self.booking.reference,
            "cancellation_type": CancellationRequest.TYPE_FULL,
            "idempotency_key": "api-idem-list",
        }
        self.client.post("/api/v1/cancellations/requests/initiate/", payload, format="json")
        resp = self.client.get("/api/v1/cancellations/requests/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
