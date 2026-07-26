import uuid

from django.conf import settings
from django.db import models

from booking.models import Booking, BookingPassenger


class CancellationRequest(models.Model):
    TYPE_FULL = "full"
    TYPE_PARTIAL_PASSENGERS = "partial_passengers"
    TYPE_PARTIAL_SEGMENTS = "partial_segments"
    CANCELLATION_TYPES = (
        (TYPE_FULL, "Full Booking Cancellation"),
        (TYPE_PARTIAL_PASSENGERS, "Partial – Passenger-wise"),
        (TYPE_PARTIAL_SEGMENTS, "Partial – Segment-wise"),
    )

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_FAILED = "failed"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_FAILED, "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="cancellation_requests")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cancellation_requests",
    )
    cancellation_type = models.CharField(max_length=30, choices=CANCELLATION_TYPES, default=TYPE_FULL)
    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_PENDING)

    # Partial cancellation scoping
    passengers = models.ManyToManyField(BookingPassenger, blank=True, related_name="cancellation_requests")
    cancelled_segment_indexes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of itinerary segment indexes being cancelled (for partial segment cancellation).",
    )
    reason = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    idempotency_key = models.CharField(max_length=128, unique=True)

    # Provider response
    provider_cancellation_reference = models.CharField(max_length=100, blank=True, default="")
    provider_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cancellation_request"
        ordering = ("-created_at",)

    def __str__(self):
        return f"CancellationRequest({self.booking.reference}, {self.cancellation_type}, {self.status})"


class RefundClaim(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_SETTLED = "settled"
    STATUS_FAILED = "failed"
    STATUS_WAIVED = "waived"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SETTLED, "Settled"),
        (STATUS_FAILED, "Failed"),
        (STATUS_WAIVED, "Waived"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="refund_claims")
    cancellation_request = models.OneToOneField(
        CancellationRequest,
        on_delete=models.PROTECT,
        related_name="refund_claim",
    )

    currency = models.CharField(max_length=3)

    # Financial breakdown
    gross_fare = models.DecimalField(max_digits=14, decimal_places=2, help_text="Total fare paid by the customer.")
    airline_penalty = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="GDS/Airline cancellation fee.")
    ota_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="OTA service/processing fee.")
    net_refund = models.DecimalField(max_digits=14, decimal_places=2, help_text="Amount to be refunded to the customer.")

    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_PENDING)
    refund_method = models.CharField(max_length=50, blank=True, help_text="e.g., original_payment, credit_wallet")
    gateway_reference = models.CharField(max_length=150, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "refund_claim"
        ordering = ("-created_at",)

    def __str__(self):
        return f"RefundClaim({self.booking.reference}, net={self.net_refund} {self.currency}, {self.status})"


class RefundLedgerEntry(models.Model):
    TYPE_AIRLINE_CREDIT = "airline_credit"
    TYPE_PENALTY = "penalty"
    TYPE_OTA_FEE = "ota_fee"
    TYPE_CUSTOMER_PAYOUT = "customer_payout"
    TYPES = (
        (TYPE_AIRLINE_CREDIT, "Airline Credit"),
        (TYPE_PENALTY, "Penalty Deduction"),
        (TYPE_OTA_FEE, "OTA Processing Fee"),
        (TYPE_CUSTOMER_PAYOUT, "Customer Payout"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund_claim = models.ForeignKey(RefundClaim, on_delete=models.PROTECT, related_name="ledger_entries")
    entry_type = models.CharField(max_length=30, choices=TYPES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refund_ledger_entry"
        ordering = ("created_at",)

    def __str__(self):
        return f"LedgerEntry({self.entry_type}, {self.amount} {self.currency})"


class CancellationAuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cancellation_request = models.ForeignKey(
        CancellationRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    refund_claim = models.ForeignKey(
        RefundClaim,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cancellation_audit_events",
    )
    action = models.CharField(max_length=100)
    status_from = models.CharField(max_length=50, blank=True)
    status_to = models.CharField(max_length=50, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cancellation_audit_event"
        ordering = ("created_at",)

    def __str__(self):
        return f"CancellationAudit({self.action}, {self.created_at})"
