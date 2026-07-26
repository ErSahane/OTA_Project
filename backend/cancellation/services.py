import logging
import secrets
from contextlib import contextmanager
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import AuditLog
from booking.models import Booking, BookingPassenger
from integrations.models import ProviderConfiguration
from integrations.services import ProviderService
from pricing.models import FarePolicy
from ticketing.models import Ticket
from ticketing.services import TicketingService

from .models import (
    CancellationAuditEvent,
    CancellationRequest,
    RefundClaim,
    RefundLedgerEntry,
)
from .signals import (
    cancellation_approved,
    cancellation_initiated,
    cancellation_rejected,
    refund_settled,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Distributed lock (re-used pattern consistent with booking and ticketing)
# ---------------------------------------------------------------------------

class DistributedLock:
    def __init__(self, name: str, timeout: int = 60):
        self.name = f"cancellation-lock:{name}"
        self.timeout = timeout

    @contextmanager
    def acquire(self):
        locked = cache.add(self.name, "1", timeout=self.timeout)
        if not locked:
            raise ValidationError("A cancellation operation for this booking is already in progress.")
        try:
            yield
        finally:
            cache.delete(self.name)


# ---------------------------------------------------------------------------
# Refund Eligibility Engine
# ---------------------------------------------------------------------------

class RefundEligibilityEngine:
    """
    Determines whether a booking / fare is eligible for a refund and
    returns the applicable airline cancellation penalty.

    Policy is loaded from FarePolicy linked through the booking session's
    pricing_request.fare_policy_code.  If no policy exists, a sensible
    default (non-refundable) is applied.
    """

    @staticmethod
    def evaluate(booking: Booking) -> dict:
        """
        Returns:
            {
                "eligible": bool,
                "refundable": bool,
                "cancellation_allowed": bool,
                "airline_penalty": Decimal,
                "policy_code": str,
                "reason": str,
            }
        """
        policy_code = ""
        fare_policy = None

        # Try to resolve FarePolicy from the booking session
        if booking.session:
            pricing_request = booking.session.pricing_request or {}
            policy_code = pricing_request.get("fare_policy_code", "")
            if policy_code:
                fare_policy = FarePolicy.objects.filter(code=policy_code, active=True).first()

        if fare_policy is None:
            # No policy found — treat as non-refundable for safety
            return {
                "eligible": False,
                "refundable": False,
                "cancellation_allowed": False,
                "airline_penalty": Decimal("0.00"),
                "policy_code": policy_code,
                "reason": "No active fare policy found. Booking treated as non-refundable.",
            }

        if not fare_policy.cancellation_allowed:
            return {
                "eligible": False,
                "refundable": False,
                "cancellation_allowed": False,
                "airline_penalty": Decimal("0.00"),
                "policy_code": policy_code,
                "reason": f"Fare policy '{policy_code}' does not permit cancellation.",
            }

        return {
            "eligible": True,
            "refundable": fare_policy.refundable,
            "cancellation_allowed": True,
            "airline_penalty": Decimal(str(fare_policy.cancellation_penalty)),
            "policy_code": policy_code,
            "reason": "Eligible for cancellation per fare policy.",
        }


# ---------------------------------------------------------------------------
# Refund Calculation Engine
# ---------------------------------------------------------------------------

class RefundCalculationEngine:
    """
    Calculates the net refund amount for full or partial cancellations.

    For partial cancellations the gross fare is pro-rated by the number of
    passengers or segments being cancelled.
    """

    # Default OTA processing fee per cancellation request (configurable)
    DEFAULT_OTA_FEE = Decimal("10.00")

    @classmethod
    def calculate(
        cls,
        booking: Booking,
        airline_penalty: Decimal,
        cancelled_passenger_count: int = 0,
        total_passenger_count: int = 0,
        ota_fee: Decimal | None = None,
    ) -> dict:
        """
        Returns a financial breakdown dict.
        """
        if ota_fee is None:
            ota_fee = cls.DEFAULT_OTA_FEE

        gross_fare = booking.total_amount

        # Pro-rate for partial cancellations
        if cancelled_passenger_count and total_passenger_count and cancelled_passenger_count < total_passenger_count:
            ratio = Decimal(cancelled_passenger_count) / Decimal(total_passenger_count)
            gross_fare = (booking.total_amount * ratio).quantize(Decimal("0.01"))
            # Also pro-rate the airline penalty per the cancelled share
            airline_penalty = (airline_penalty * ratio).quantize(Decimal("0.01"))

        net_refund = gross_fare - airline_penalty - ota_fee
        if net_refund < Decimal("0.00"):
            net_refund = Decimal("0.00")

        return {
            "gross_fare": gross_fare,
            "airline_penalty": airline_penalty,
            "ota_fee": ota_fee,
            "net_refund": net_refund,
            "currency": booking.currency,
        }


# ---------------------------------------------------------------------------
# Cancellation Workflow
# ---------------------------------------------------------------------------

class CancellationWorkflow:

    # -----------------------------------------------------------------------
    # Initiation
    # -----------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def initiate_cancellation(
        cls,
        booking: Booking,
        cancellation_type: str,
        idempotency_key: str,
        passenger_ids: list[str] | None = None,
        segment_indexes: list[int] | None = None,
        reason: str = "",
        user=None,
    ) -> dict:
        """
        Creates a CancellationRequest in PENDING status and returns a
        refund estimate.  Does NOT contact the GDS provider at this stage.

        Returns:
            {
                "cancellation_request": CancellationRequest,
                "eligibility": dict,
                "estimate": dict,
            }
        """
        # Idempotency guard
        existing = CancellationRequest.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return {
                "cancellation_request": existing,
                "eligibility": RefundEligibilityEngine.evaluate(booking),
                "estimate": cls._build_estimate(booking, existing, RefundEligibilityEngine.evaluate(booking)),
            }

        # Validate booking status
        if booking.status == Booking.STATUS_CANCELLED:
            raise ValidationError("Booking is already cancelled.")
        if booking.status not in (Booking.STATUS_CONFIRMED, Booking.STATUS_PENDING, Booking.STATUS_HELD):
            raise ValidationError(f"Booking status '{booking.status}' cannot be cancelled.")

        # Eligibility check
        eligibility = RefundEligibilityEngine.evaluate(booking)
        if not eligibility["eligible"]:
            raise ValidationError(eligibility["reason"])

        # Resolve passengers for partial cancellations
        passengers_qs = BookingPassenger.objects.none()
        if cancellation_type == CancellationRequest.TYPE_PARTIAL_PASSENGERS and passenger_ids:
            passengers_qs = BookingPassenger.objects.filter(
                id__in=passenger_ids, booking=booking
            )
            if not passengers_qs.exists():
                raise ValidationError("No valid passengers found for the given IDs.")

        cancellation_request = CancellationRequest.objects.create(
            booking=booking,
            requested_by=user,
            cancellation_type=cancellation_type,
            status=CancellationRequest.STATUS_PENDING,
            cancelled_segment_indexes=segment_indexes or [],
            reason=reason,
            idempotency_key=idempotency_key,
        )

        if passengers_qs.exists():
            cancellation_request.passengers.set(passengers_qs)

        cls._audit(
            "cancellation.initiated",
            cancellation_request=cancellation_request,
            user=user,
            status_to=CancellationRequest.STATUS_PENDING,
            details={"type": cancellation_type, "reason": reason},
        )

        estimate = cls._build_estimate(booking, cancellation_request, eligibility)

        # Signal
        cancellation_initiated.send(
            sender=cls,
            cancellation_request=cancellation_request,
            booking=booking,
        )

        return {
            "cancellation_request": cancellation_request,
            "eligibility": eligibility,
            "estimate": estimate,
        }

    # -----------------------------------------------------------------------
    # Approval / Processing
    # -----------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def process_cancellation(cls, cancellation_request: CancellationRequest, user=None) -> RefundClaim:
        """
        Executes the full GDS cancellation, voids local tickets, creates the
        RefundClaim, posts ledger entries, and transitions statuses atomically.

        Idempotent: returns the existing RefundClaim if already processed.
        """
        if cancellation_request.status == CancellationRequest.STATUS_APPROVED:
            return cancellation_request.refund_claim

        if cancellation_request.status != CancellationRequest.STATUS_PENDING:
            raise ValidationError(
                f"Cannot process a cancellation request with status '{cancellation_request.status}'."
            )

        booking = cancellation_request.booking

        with DistributedLock(str(cancellation_request.id)).acquire():
            # Re-fetch after acquiring lock
            cancellation_request.refresh_from_db()
            if cancellation_request.status == CancellationRequest.STATUS_APPROVED:
                return cancellation_request.refund_claim

            # Provider cancellation
            config = ProviderConfiguration.objects.filter(
                provider_name=booking.provider_name, enabled=True
            ).first()
            if not config:
                raise ValidationError(
                    f"Provider configuration for '{booking.provider_name}' not found."
                )

            provider_payload = {
                "booking_reference": booking.provider_booking_reference,
                "cancellation_type": cancellation_request.cancellation_type,
                "passenger_ids": [
                    str(p.id) for p in cancellation_request.passengers.all()
                ],
                "segment_indexes": cancellation_request.cancelled_segment_indexes,
            }
            response = ProviderService(config).cancel_booking(provider_payload)

            if response.get("status") != "ok":
                previous = cancellation_request.status
                cancellation_request.status = CancellationRequest.STATUS_FAILED
                cancellation_request.provider_response = response
                cancellation_request.save(update_fields=["status", "provider_response", "updated_at"])
                cls._audit(
                    "cancellation.provider.failed",
                    cancellation_request=cancellation_request,
                    user=user,
                    status_from=previous,
                    status_to=CancellationRequest.STATUS_FAILED,
                    details=response,
                )
                raise ValidationError(
                    response.get("error", {}).get("message", "GDS cancellation failed.")
                )

            cancellation_request.provider_cancellation_reference = response.get(
                "booking_reference", ""
            )
            cancellation_request.provider_response = response

            # Void local tickets
            cls._void_relevant_tickets(cancellation_request, user)

            # Calculate refund
            eligibility = RefundEligibilityEngine.evaluate(booking)
            cancelled_pax_count = cancellation_request.passengers.count()
            total_pax_count = booking.passengers.count()

            financial = RefundCalculationEngine.calculate(
                booking=booking,
                airline_penalty=eligibility["airline_penalty"],
                cancelled_passenger_count=cancelled_pax_count,
                total_passenger_count=total_pax_count,
            )

            # Create RefundClaim
            refund_claim = RefundClaim.objects.create(
                booking=booking,
                cancellation_request=cancellation_request,
                currency=financial["currency"],
                gross_fare=financial["gross_fare"],
                airline_penalty=financial["airline_penalty"],
                ota_fee=financial["ota_fee"],
                net_refund=financial["net_refund"],
                status=RefundClaim.STATUS_PENDING,
                refund_method="original_payment",
            )

            # Post ledger entries
            cls._post_ledger(refund_claim, financial)

            # Transition booking status for full cancellations
            if cancellation_request.cancellation_type == CancellationRequest.TYPE_FULL:
                booking.status = Booking.STATUS_CANCELLED
                booking.save(update_fields=["status", "updated_at"])

            # Approve the request
            previous = cancellation_request.status
            cancellation_request.status = CancellationRequest.STATUS_APPROVED
            cancellation_request.save(update_fields=["status", "provider_cancellation_reference", "provider_response", "updated_at"])

            cls._audit(
                "cancellation.approved",
                cancellation_request=cancellation_request,
                refund_claim=refund_claim,
                user=user,
                status_from=previous,
                status_to=CancellationRequest.STATUS_APPROVED,
                details={
                    "net_refund": str(financial["net_refund"]),
                    "currency": financial["currency"],
                },
            )

            # Signals
            cancellation_approved.send(
                sender=cls,
                cancellation_request=cancellation_request,
                refund_claim=refund_claim,
                booking=booking,
            )

            return refund_claim

    # -----------------------------------------------------------------------
    # Rejection
    # -----------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def reject_cancellation(
        cls,
        cancellation_request: CancellationRequest,
        rejection_reason: str = "",
        user=None,
    ) -> CancellationRequest:
        if cancellation_request.status != CancellationRequest.STATUS_PENDING:
            raise ValidationError(
                f"Only PENDING cancellation requests can be rejected. Current: '{cancellation_request.status}'."
            )

        previous = cancellation_request.status
        cancellation_request.status = CancellationRequest.STATUS_REJECTED
        cancellation_request.rejection_reason = rejection_reason
        cancellation_request.save(update_fields=["status", "rejection_reason", "updated_at"])

        cls._audit(
            "cancellation.rejected",
            cancellation_request=cancellation_request,
            user=user,
            status_from=previous,
            status_to=CancellationRequest.STATUS_REJECTED,
            details={"rejection_reason": rejection_reason},
        )

        cancellation_rejected.send(
            sender=cls,
            cancellation_request=cancellation_request,
            booking=cancellation_request.booking,
        )
        return cancellation_request

    # -----------------------------------------------------------------------
    # Refund Settlement (simulated — real integration handled externally)
    # -----------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def settle_refund(cls, refund_claim: RefundClaim, gateway_reference: str = "", user=None) -> RefundClaim:
        if refund_claim.status == RefundClaim.STATUS_SETTLED:
            return refund_claim
        if refund_claim.status not in (RefundClaim.STATUS_PENDING, RefundClaim.STATUS_PROCESSING):
            raise ValidationError(
                f"Cannot settle a refund claim with status '{refund_claim.status}'."
            )

        previous = refund_claim.status
        refund_claim.status = RefundClaim.STATUS_SETTLED
        refund_claim.gateway_reference = gateway_reference or f"GW-{secrets.token_hex(6).upper()}"
        refund_claim.settled_at = timezone.now()
        refund_claim.save(update_fields=["status", "gateway_reference", "settled_at", "updated_at"])

        cls._audit(
            "refund.settled",
            refund_claim=refund_claim,
            user=user,
            status_from=previous,
            status_to=RefundClaim.STATUS_SETTLED,
            details={"gateway_reference": refund_claim.gateway_reference},
        )

        refund_settled.send(
            sender=cls,
            refund_claim=refund_claim,
            booking=refund_claim.booking,
        )
        return refund_claim

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _void_relevant_tickets(cancellation_request: CancellationRequest, user=None):
        """
        Voids tickets for the passengers in scope of the cancellation.
        For full cancellations, all issued tickets are voided.
        """
        booking = cancellation_request.booking
        issued_tickets = Ticket.objects.filter(
            booking=booking, status=Ticket.STATUS_ISSUED
        )

        if cancellation_request.cancellation_type == CancellationRequest.TYPE_PARTIAL_PASSENGERS:
            passenger_ids = list(cancellation_request.passengers.values_list("id", flat=True))
            issued_tickets = issued_tickets.filter(passenger__id__in=passenger_ids)

        for ticket in issued_tickets:
            try:
                TicketingService.void_ticket(ticket, user=user)
            except Exception as exc:
                logger.warning(f"Could not void ticket {ticket.ticket_number}: {exc}")

    @staticmethod
    def _post_ledger(refund_claim: RefundClaim, financial: dict):
        """Posts the four double-entry ledger lines for a refund claim."""
        entries = [
            (RefundLedgerEntry.TYPE_AIRLINE_CREDIT, financial["gross_fare"], "Gross fare credited from airline/GDS"),
            (RefundLedgerEntry.TYPE_PENALTY, -financial["airline_penalty"], "Airline cancellation penalty deducted"),
            (RefundLedgerEntry.TYPE_OTA_FEE, -financial["ota_fee"], "OTA processing fee deducted"),
            (RefundLedgerEntry.TYPE_CUSTOMER_PAYOUT, financial["net_refund"], "Net refund to customer"),
        ]
        for entry_type, amount, description in entries:
            RefundLedgerEntry.objects.create(
                refund_claim=refund_claim,
                entry_type=entry_type,
                amount=amount,
                currency=financial["currency"],
                description=description,
            )

    @staticmethod
    def _build_estimate(booking: Booking, cancellation_request: CancellationRequest, eligibility: dict) -> dict:
        cancelled_pax = cancellation_request.passengers.count()
        total_pax = booking.passengers.count()
        return RefundCalculationEngine.calculate(
            booking=booking,
            airline_penalty=eligibility["airline_penalty"],
            cancelled_passenger_count=cancelled_pax,
            total_passenger_count=total_pax,
        )

    @staticmethod
    def _audit(
        action: str,
        cancellation_request: CancellationRequest | None = None,
        refund_claim: RefundClaim | None = None,
        user=None,
        status_from: str = "",
        status_to: str = "",
        details: dict | None = None,
    ):
        details = details or {}
        CancellationAuditEvent.objects.create(
            cancellation_request=cancellation_request,
            refund_claim=refund_claim,
            user=user,
            action=action,
            status_from=status_from,
            status_to=status_to,
            details=details,
        )
        AuditLog.objects.create(user=user, action=action, details=str(details))
