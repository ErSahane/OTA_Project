import logging
import secrets
import string
from contextlib import contextmanager
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import AuditLog
from booking.models import Booking
from integrations.models import ProviderConfiguration
from integrations.services import ProviderService

from .models import PNRRecord, Ticket, TicketAuditEvent
from .signals import pnr_synced, ticket_issued, ticket_reissued, ticket_voided

logger = logging.getLogger(__name__)


class DistributedLock:
    def __init__(self, name, timeout=30):
        self.name = f"ticketing-lock:{name}"
        self.timeout = timeout

    @contextmanager
    def acquire(self):
        locked = cache.add(self.name, "1", timeout=self.timeout)
        if not locked:
            raise ValidationError("A ticketing request for this booking is already in progress.")
        try:
            yield
        finally:
            cache.delete(self.name)


class TicketPDFGenerator:
    @staticmethod
    def generate_html(ticket: Ticket) -> str:
        booking = ticket.booking
        passenger = ticket.passenger
        pnr = ticket.pnr_record

        segments_html = ""
        segments = pnr.itinerary_data.get("segments", [])
        for seg in segments:
            carrier = seg.get("carrier", "AV")
            flight_number = seg.get("flight_number", "101")
            origin = seg.get("origin", "LHR")
            destination = seg.get("destination", "JFK")
            dep_time = seg.get("departure_time", "N/A")
            arr_time = seg.get("arrival_time", "N/A")
            cls_service = seg.get("class_of_service", "Y")
            status = seg.get("status", "Confirmed")

            segments_html += f"""
            <tr>
                <td>{carrier}{flight_number}</td>
                <td>{origin}</td>
                <td>{destination}</td>
                <td>{dep_time}</td>
                <td>{arr_time}</td>
                <td>{cls_service}</td>
                <td>{status}</td>
            </tr>
            """

        invoice = pnr.invoice_data
        base_fare = invoice.get("base_fare", "0.00")
        taxes_and_fees = invoice.get("taxes_and_fees", "0.00")
        grand_total = invoice.get("grand_total", "0.00")
        currency = booking.currency

        issued_at_str = ticket.issued_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.issued_at else "N/A"

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AstraVoyage E-Ticket Receipt</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 30px; color: #333; line-height: 1.4; }}
        .header {{ border-bottom: 3px solid #0056b3; padding-bottom: 12px; margin-bottom: 25px; }}
        .logo {{ font-size: 26px; font-weight: bold; color: #0056b3; text-transform: uppercase; }}
        .ticket-info {{ display: flex; justify-content: space-between; margin-bottom: 25px; background: #f8f9fa; padding: 15px; border-radius: 4px; }}
        .ticket-info div {{ flex: 1; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #0056b3; margin-top: 25px; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; }}
        th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: left; }}
        th {{ background-color: #f1f3f5; font-weight: 600; }}
        .totals-table td {{ border: none; padding: 6px 10px; }}
        .totals-table tr.grand-total td {{ font-weight: bold; font-size: 16px; border-top: 1px solid #dee2e6; padding-top: 10px; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #6c757d; border-top: 1px solid #dee2e6; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="logo">AstraVoyage E-Ticket Receipt</span>
    </div>
    <div class="ticket-info">
        <div>
            <strong>Passenger:</strong> {passenger.first_name} {passenger.last_name}<br>
            <strong>Ticket Number:</strong> {ticket.ticket_number}<br>
            <strong>Booking Reference:</strong> {booking.reference}
        </div>
        <div>
            <strong>GDS PNR:</strong> {pnr.provider_pnr}<br>
            <strong>Internal Reference:</strong> {pnr.internal_reference}<br>
            <strong>Issue Date:</strong> {issued_at_str}
        </div>
    </div>
    
    <div class="section-title">Itinerary Details</div>
    <table>
        <thead>
            <tr>
                <th>Flight</th>
                <th>From</th>
                <th>To</th>
                <th>Departure</th>
                <th>Arrival</th>
                <th>Class</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {segments_html}
        </tbody>
    </table>
    
    <div class="section-title">Invoice Summary</div>
    <table class="totals-table" style="max-width: 400px; margin-left: auto;">
        <tr>
            <td>Base Fare:</td>
            <td style="text-align: right;">{base_fare} {currency}</td>
        </tr>
        <tr>
            <td>Taxes & Fees:</td>
            <td style="text-align: right;">{taxes_and_fees} {currency}</td>
        </tr>
        <tr class="grand-total">
            <td>Grand Total:</td>
            <td style="text-align: right;">{grand_total} {currency}</td>
        </tr>
    </table>
    
    <div class="footer">
        <p>* Carriage and other services provided by the carrier are subject to conditions of carriage.</p>
        <p>* Thank you for choosing AstraVoyage.</p>
    </div>
</body>
</html>
"""


class PNRManager:
    @staticmethod
    def generate_internal_reference() -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            ref = "AV" + "".join(secrets.choice(alphabet) for _ in range(4))
            if not PNRRecord.objects.filter(internal_reference=ref).exists():
                return ref

    @classmethod
    @transaction.atomic
    def sync_pnr(cls, pnr_record: PNRRecord, user=None) -> PNRRecord:
        config = ProviderConfiguration.objects.filter(provider_name=pnr_record.provider_name, enabled=True).first()
        if not config:
            raise ValidationError(f"Provider configuration for {pnr_record.provider_name} not found.")

        payload = {
            "provider_booking_reference": pnr_record.booking.provider_booking_reference,
            "provider_pnr": pnr_record.provider_pnr,
        }

        response = ProviderService(config).sync_pnr(payload)
        if response.get("status") != "ok":
            pnr_record.status = PNRRecord.STATUS_FAILED
            pnr_record.save(update_fields=["status", "updated_at"])
            cls._audit("pnr.sync.failed", pnr_record=pnr_record, user=user, status_from=PNRRecord.STATUS_PENDING, status_to=PNRRecord.STATUS_FAILED, details=response)
            raise ValidationError(response.get("error", {}).get("message", "GDS PNR Sync failed."))

        previous_status = pnr_record.status
        pnr_record.status = PNRRecord.STATUS_SYNCED
        pnr_record.synced_at = timezone.now()

        # Update segments if GDS returned them
        itinerary = response.get("itinerary", {})
        if itinerary:
            pnr_record.itinerary_data = itinerary

        pnr_record.save()

        cls._audit("pnr.synced", pnr_record=pnr_record, user=user, status_from=previous_status, status_to=pnr_record.status, details={"pnr": pnr_record.provider_pnr})

        # Emit signal
        pnr_synced.send(sender=cls, pnr_record=pnr_record, booking=pnr_record.booking)
        return pnr_record

    @staticmethod
    def _audit(action, pnr_record=None, user=None, status_from="", status_to="", details=None):
        details = details or {}
        TicketAuditEvent.objects.create(
            pnr_record=pnr_record,
            user=user,
            action=action,
            status_from=status_from,
            status_to=status_to,
            details=details,
        )
        AuditLog.objects.create(user=user, action=action, details=str(details))


class TicketingService:
    @classmethod
    @transaction.atomic
    def issue_tickets(cls, booking: Booking, idempotency_key: str, user=None) -> list[Ticket]:
        # Lock to ensure ticket issuance is idempotent
        with DistributedLock(booking.reference).acquire():
            # Check if tickets have already been issued with this idempotency key
            existing_tickets = Ticket.objects.filter(booking=booking, idempotency_key__startswith=idempotency_key)
            if existing_tickets.exists():
                logger.info(f"Tickets already issued under idempotency key {idempotency_key}")
                return list(existing_tickets)

            if booking.status not in (Booking.STATUS_PENDING, Booking.STATUS_HELD, Booking.STATUS_CONFIRMED):
                raise ValidationError(f"Invalid booking status '{booking.status}' for ticket issuance.")

            config = ProviderConfiguration.objects.filter(provider_name=booking.provider_name, enabled=True).first()
            if not config:
                raise ValidationError(f"Provider configuration for {booking.provider_name} not found.")

            # Ensure PNRRecord exists
            pnr_record, created = PNRRecord.objects.get_or_create(
                booking=booking,
                defaults={
                    "internal_reference": PNRManager.generate_internal_reference(),
                    "provider_name": booking.provider_name,
                    "provider_pnr": booking.provider_booking_reference or "MOCKPNR",
                    "status": PNRRecord.STATUS_PENDING,
                },
            )

            passengers = list(booking.passengers.all())
            if not passengers:
                raise ValidationError("Booking has no passengers to ticket.")

            issued_tickets = []

            # Issue ticket at GDS per passenger
            for index, passenger in enumerate(passengers):
                issue_payload = {
                    "booking_reference": booking.provider_booking_reference,
                    "passenger_index": index,
                    "first_name": passenger.first_name,
                    "last_name": passenger.last_name,
                    "passenger_type": passenger.passenger_type,
                }
                response = ProviderService(config).issue_ticket(issue_payload)
                if response.get("status") != "ok":
                    cls._audit("ticket.issue.failed", pnr_record=pnr_record, user=user, details={"error": response, "passenger": passenger.id})
                    raise ValidationError(response.get("error", {}).get("message", "GDS Ticket Issuance failed."))

                ticket_num = response.get("ticket_number") or f"176{secrets.token_hex(5)}"
                ticket = Ticket.objects.create(
                    booking=booking,
                    passenger=passenger,
                    pnr_record=pnr_record,
                    idempotency_key=f"{idempotency_key}:{passenger.id}",
                    ticket_number=ticket_num,
                    provider_ticket_number=ticket_num,
                    status=Ticket.STATUS_ISSUED,
                    coupon_data={"status": "OK", "coupons": [{"coupon_number": 1, "status": "Open"}]},
                    issued_at=timezone.now(),
                )

                issued_tickets.append(ticket)

            # Build itinerary and invoice data
            cls._build_itinerary_and_invoice(pnr_record, booking)

            # Generate PDF representation for each ticket
            for ticket in issued_tickets:
                ticket.pdf_content = TicketPDFGenerator.generate_html(ticket)
                ticket.save(update_fields=["pdf_content"])

            # Finalize PNRRecord sync status
            pnr_record.status = PNRRecord.STATUS_SYNCED
            pnr_record.synced_at = timezone.now()
            pnr_record.save(update_fields=["status", "synced_at", "itinerary_data", "invoice_data"])

            # Confirm Booking completion
            booking.status = Booking.STATUS_CONFIRMED
            booking.save(update_fields=["status", "updated_at"])

            # Log events
            cls._audit("booking.ticketed", pnr_record=pnr_record, user=user, details={"reference": booking.reference})
            for ticket in issued_tickets:
                cls._audit("ticket.issued", pnr_record=pnr_record, ticket=ticket, user=user, status_to=Ticket.STATUS_ISSUED, details={"ticket_number": ticket.ticket_number})
                # Trigger signal
                ticket_issued.send(sender=cls, ticket=ticket, booking=booking)

            return issued_tickets

    @classmethod
    @transaction.atomic
    def void_ticket(cls, ticket: Ticket, user=None) -> Ticket:
        if ticket.status != Ticket.STATUS_ISSUED:
            raise ValidationError(f"Only tickets in ISSUED status can be voided. Current: {ticket.status}")

        config = ProviderConfiguration.objects.filter(provider_name=ticket.booking.provider_name, enabled=True).first()
        if not config:
            raise ValidationError(f"Provider configuration for {ticket.booking.provider_name} not found.")

        payload = {"ticket_number": ticket.ticket_number, "pnr": ticket.pnr_record.provider_pnr}
        response = ProviderService(config).void_ticket(payload)
        if response.get("status") != "ok":
            cls._audit("ticket.void.failed", pnr_record=ticket.pnr_record, ticket=ticket, user=user, details=response)
            raise ValidationError(response.get("error", {}).get("message", "GDS Ticket Void failed."))

        previous_status = ticket.status
        ticket.status = Ticket.STATUS_VOIDED
        ticket.voided_at = timezone.now()
        ticket.save(update_fields=["status", "voided_at", "updated_at"])

        # Update coupons to voided
        ticket.coupon_data = {"status": "VOIDED", "coupons": [{"coupon_number": 1, "status": "Voided"}]}
        ticket.save(update_fields=["coupon_data"])

        cls._audit("ticket.voided", pnr_record=ticket.pnr_record, ticket=ticket, user=user, status_from=previous_status, status_to=ticket.status)

        # Trigger signal
        ticket_voided.send(sender=cls, ticket=ticket, booking=ticket.booking)
        return ticket

    @classmethod
    @transaction.atomic
    def reissue_ticket(cls, old_ticket: Ticket, new_pricing_payload: dict, idempotency_key: str, user=None) -> Ticket:
        if old_ticket.status != Ticket.STATUS_ISSUED:
            raise ValidationError(f"Only tickets in ISSUED status can be reissued. Current: {old_ticket.status}")

        existing_reissue = Ticket.objects.filter(reissue_parent=old_ticket, idempotency_key=idempotency_key).first()
        if existing_reissue:
            return existing_reissue

        config = ProviderConfiguration.objects.filter(provider_name=old_ticket.booking.provider_name, enabled=True).first()
        if not config:
            raise ValidationError(f"Provider configuration for {old_ticket.booking.provider_name} not found.")

        # Request new ticket from GDS referencing exchange/reissue
        reissue_payload = {
            "old_ticket_number": old_ticket.ticket_number,
            "pnr": old_ticket.pnr_record.provider_pnr,
            "new_pricing": new_pricing_payload,
        }
        response = ProviderService(config).issue_ticket(reissue_payload)
        if response.get("status") != "ok":
            cls._audit("ticket.reissue.failed", pnr_record=old_ticket.pnr_record, ticket=old_ticket, user=user, details=response)
            raise ValidationError(response.get("error", {}).get("message", "GDS Ticket Reissue failed."))

        new_ticket_num = response.get("ticket_number") or f"176{secrets.token_hex(5)}"

        # Mark old ticket reissued
        previous_status = old_ticket.status
        old_ticket.status = Ticket.STATUS_REISSUED
        old_ticket.save(update_fields=["status", "updated_at"])

        cls._audit("ticket.reissued.parent", pnr_record=old_ticket.pnr_record, ticket=old_ticket, user=user, status_from=previous_status, status_to=old_ticket.status)

        # Create new reissued ticket
        new_ticket = Ticket.objects.create(
            booking=old_ticket.booking,
            passenger=old_ticket.passenger,
            pnr_record=old_ticket.pnr_record,
            idempotency_key=idempotency_key,
            ticket_number=new_ticket_num,
            provider_ticket_number=new_ticket_num,
            status=Ticket.STATUS_ISSUED,
            coupon_data={"status": "OK", "coupons": [{"coupon_number": 1, "status": "Open"}]},
            reissue_parent=old_ticket,
            issued_at=timezone.now(),
        )

        # Regenerate PDF for the new ticket
        new_ticket.pdf_content = TicketPDFGenerator.generate_html(new_ticket)
        new_ticket.save(update_fields=["pdf_content"])

        cls._audit("ticket.reissued.child", pnr_record=old_ticket.pnr_record, ticket=new_ticket, user=user, status_to=Ticket.STATUS_ISSUED, details={"reissue_parent": old_ticket.ticket_number})

        # Trigger signal
        ticket_reissued.send(sender=cls, old_ticket=old_ticket, new_ticket=new_ticket, booking=old_ticket.booking)
        return new_ticket

    @classmethod
    def _build_itinerary_and_invoice(cls, pnr_record: PNRRecord, booking: Booking):
        # Default mock segments if none exist in the session
        segments = []
        session = booking.session
        selected_offer = session.selected_offer if session else {}
        flights = selected_offer.get("flights", [])

        if flights:
            for f in flights:
                segments.append({
                    "carrier": f.get("carrier", "AV"),
                    "flight_number": f.get("flight_number", "101"),
                    "origin": f.get("origin", "LHR"),
                    "destination": f.get("destination", "JFK"),
                    "departure_time": f.get("departure_time", (timezone.now() + timezone.timedelta(days=7)).isoformat()),
                    "arrival_time": f.get("arrival_time", (timezone.now() + timezone.timedelta(days=7, hours=8)).isoformat()),
                    "class_of_service": f.get("class", "Y"),
                    "status": "Confirmed"
                })
        else:
            segments.append({
                "carrier": "AV",
                "flight_number": "101",
                "origin": "LHR",
                "destination": "JFK",
                "departure_time": (timezone.now() + timezone.timedelta(days=7)).isoformat(),
                "arrival_time": (timezone.now() + timezone.timedelta(days=7, hours=8)).isoformat(),
                "class_of_service": "Y",
                "status": "Confirmed"
            })

        pnr_record.itinerary_data = {"segments": segments}

        # Calculate fare totals
        base_fare = booking.total_amount * Decimal("0.85")
        taxes_and_fees = booking.total_amount * Decimal("0.15")

        pnr_record.invoice_data = {
            "invoice_number": f"INV{secrets.token_hex(4).upper()}",
            "base_fare": str(base_fare.quantize(Decimal("0.01"))),
            "taxes_and_fees": str(taxes_and_fees.quantize(Decimal("0.01"))),
            "grand_total": str(booking.total_amount.quantize(Decimal("0.01"))),
            "payment_status": "Paid",
            "billed_to": f"{booking.contact_first_name} {booking.contact_last_name}",
        }

    @staticmethod
    def _audit(action, pnr_record=None, ticket=None, user=None, status_from="", status_to="", details=None):
        details = details or {}
        TicketAuditEvent.objects.create(
            pnr_record=pnr_record,
            ticket=ticket,
            user=user,
            action=action,
            status_from=status_from,
            status_to=status_to,
            details=details,
        )
        AuditLog.objects.create(user=user, action=action, details=str(details))
