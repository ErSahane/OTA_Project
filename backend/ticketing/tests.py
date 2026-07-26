from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from booking.models import Booking, BookingPassenger, BookingSession
from integrations.models import ProviderConfiguration

from .models import PNRRecord, Ticket, TicketAuditEvent
from .services import PNRManager, TicketingService

User = get_user_model()


class TicketingEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="traveler@example.com", username="traveler", password="pass12345")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        self.provider_config = ProviderConfiguration.objects.create(provider_name="mock-provider", provider_type="mock")

        # Setup baseline booking session
        self.session = BookingSession.objects.create(
            user=self.user,
            session_token="sess-token-1",
            booking_token="b-token-1",
            idempotency_key="idem-key-1",
            provider_name="mock-provider",
            quoted_total=Decimal("200.00"),
            currency="USD",
            contact_email="passenger@example.com",
            contact_phone="+12345678",
            contact_first_name="Jane",
            contact_last_name="Doe",
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
        )

        # Setup baseline booking
        self.booking = Booking.objects.create(
            session=self.session,
            user=self.user,
            reference="BKGTEST123",
            provider_name="mock-provider",
            provider_booking_reference="GDSREF123",
            currency="USD",
            total_amount=Decimal("200.00"),
            status=Booking.STATUS_CONFIRMED,
            contact_email="passenger@example.com",
            contact_phone="+12345678",
            contact_first_name="Jane",
            contact_last_name="Doe",
        )

        self.passenger = BookingPassenger.objects.create(
            booking=self.booking,
            passenger_type="ADT",
            title="Ms",
            first_name="Jane",
            last_name="Doe",
            gender="F",
            date_of_birth=date(1995, 5, 15),
        )

    def test_internal_reference_generation(self):
        ref = PNRManager.generate_internal_reference()
        self.assertEqual(len(ref), 6)
        self.assertTrue(ref.startswith("AV"))

    def test_ticket_issuance_success_and_idempotency(self):
        idempotency_key = "idem-ticket-issuance-test"

        # Issuance
        tickets = TicketingService.issue_tickets(self.booking, idempotency_key, user=self.user)
        self.assertEqual(len(tickets), 1)
        ticket = tickets[0]

        self.assertEqual(ticket.status, Ticket.STATUS_ISSUED)
        self.assertTrue(ticket.ticket_number.startswith("176"))
        self.assertEqual(len(ticket.ticket_number), 13)
        self.assertIn("AstraVoyage E-Ticket Receipt", ticket.pdf_content)

        # Confirm PNRRecord creation and sync status
        pnr_record = PNRRecord.objects.get(booking=self.booking)
        self.assertEqual(pnr_record.status, PNRRecord.STATUS_SYNCED)
        self.assertEqual(pnr_record.provider_pnr, "GDSREF123")
        self.assertIn("segments", pnr_record.itinerary_data)
        self.assertIn("grand_total", pnr_record.invoice_data)

        # Audit events check
        audit_events = TicketAuditEvent.objects.filter(pnr_record=pnr_record)
        self.assertTrue(audit_events.exists())

        # Second issuance request with the same idempotency key
        duplicate_tickets = TicketingService.issue_tickets(self.booking, idempotency_key, user=self.user)
        self.assertEqual(len(duplicate_tickets), 1)
        self.assertEqual(duplicate_tickets[0].id, ticket.id)

    def test_pnr_sync(self):
        pnr_record = PNRRecord.objects.create(
            booking=self.booking,
            internal_reference=PNRManager.generate_internal_reference(),
            provider_name="mock-provider",
            provider_pnr="GDSREF123",
            status=PNRRecord.STATUS_PENDING,
        )

        PNRManager.sync_pnr(pnr_record, user=self.user)
        pnr_record.refresh_from_db()

        self.assertEqual(pnr_record.status, PNRRecord.STATUS_SYNCED)
        self.assertEqual(pnr_record.itinerary_data["segments"][0]["from"], "LHR")
        self.assertEqual(pnr_record.itinerary_data["segments"][0]["to"], "JFK")
        self.assertIsNotNone(pnr_record.synced_at)

    def test_ticket_void(self):
        tickets = TicketingService.issue_tickets(self.booking, "void-idemp", user=self.user)
        ticket = tickets[0]

        voided_ticket = TicketingService.void_ticket(ticket, user=self.user)
        self.assertEqual(voided_ticket.status, Ticket.STATUS_VOIDED)
        self.assertIsNotNone(voided_ticket.voided_at)

        # Attempt to void again should fail
        with self.assertRaises(ValidationError):
            TicketingService.void_ticket(voided_ticket, user=self.user)

    def test_ticket_reissue(self):
        tickets = TicketingService.issue_tickets(self.booking, "reissue-idemp", user=self.user)
        old_ticket = tickets[0]

        reissued_ticket = TicketingService.reissue_ticket(
            old_ticket,
            new_pricing_payload={"base_fare": "150.00"},
            idempotency_key="new-reissue-idemp",
            user=self.user,
        )

        old_ticket.refresh_from_db()
        self.assertEqual(old_ticket.status, Ticket.STATUS_REISSUED)
        self.assertEqual(reissued_ticket.status, Ticket.STATUS_ISSUED)
        self.assertEqual(reissued_ticket.reissue_parent, old_ticket)

    def test_api_endpoints_flow(self):
        # 1. Issue Ticket API
        payload = {"booking_reference": self.booking.reference, "idempotency_key": "api-idem-key"}
        response = self.client.post("/api/v1/ticketing/tickets/issue/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        ticket_id = response.data[0]["id"]
        ticket_num = response.data[0]["ticket_number"]

        # 2. PDF View Endpoint
        pdf_response = self.client.get(f"/api/v1/ticketing/tickets/{ticket_id}/pdf/")
        self.assertEqual(pdf_response.status_code, 200)
        self.assertIn("AstraVoyage E-Ticket Receipt", pdf_response.content.decode("utf-8"))

        # 3. PNR Sync Action
        pnr = PNRRecord.objects.get(booking=self.booking)
        sync_response = self.client.post(f"/api/v1/ticketing/pnr/{pnr.internal_reference}/sync/")
        self.assertEqual(sync_response.status_code, 200)
        self.assertEqual(sync_response.data["status"], PNRRecord.STATUS_SYNCED)

        # 4. Reissue API Endpoint
        reissue_payload = {"new_pricing": {"base_fare": "250.00"}, "idempotency_key": "api-reissue-idem"}
        reissue_response = self.client.post(f"/api/v1/ticketing/tickets/{ticket_id}/reissue/", reissue_payload, format="json")
        self.assertEqual(reissue_response.status_code, 201)
        self.assertEqual(str(reissue_response.data["reissue_parent"]), str(ticket_id))

        # 5. Void API Endpoint
        new_ticket_id = reissue_response.data["id"]
        void_response = self.client.post(f"/api/v1/ticketing/tickets/{new_ticket_id}/void/")
        self.assertEqual(void_response.status_code, 200)
        self.assertEqual(void_response.data["status"], Ticket.STATUS_VOIDED)
