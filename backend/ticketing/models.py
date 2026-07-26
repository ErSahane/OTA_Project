import uuid

from django.conf import settings
from django.db import models

from booking.models import Booking, BookingPassenger


class PNRRecord(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SYNCED = "synced"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = ((STATUS_PENDING, "Pending"), (STATUS_SYNCED, "Synced"), (STATUS_FAILED, "Failed"), (STATUS_CANCELLED, "Cancelled"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, related_name="pnr_record", on_delete=models.CASCADE)
    internal_reference = models.CharField(max_length=32, unique=True)
    provider_name = models.CharField(max_length=100)
    provider_pnr = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    synced_at = models.DateTimeField(null=True, blank=True)
    itinerary_data = models.JSONField(default=dict, blank=True)
    invoice_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ticketing_pnr_record"
        ordering = ("-created_at",)


class Ticket(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ISSUED = "issued"
    STATUS_VOIDED = "voided"
    STATUS_REISSUED = "reissued"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = ((STATUS_PENDING, "Pending"), (STATUS_ISSUED, "Issued"), (STATUS_VOIDED, "Voided"), (STATUS_REISSUED, "Reissued"), (STATUS_FAILED, "Failed"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, related_name="tickets", on_delete=models.CASCADE)
    passenger = models.ForeignKey(BookingPassenger, related_name="tickets", on_delete=models.CASCADE)
    pnr_record = models.ForeignKey(PNRRecord, related_name="tickets", on_delete=models.CASCADE)
    idempotency_key = models.CharField(max_length=100, unique=True)
    ticket_number = models.CharField(max_length=32, unique=True)
    provider_ticket_number = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    coupon_data = models.JSONField(default=dict, blank=True)
    reissue_parent = models.ForeignKey("self", null=True, blank=True, related_name="reissues", on_delete=models.SET_NULL)
    pdf_content = models.TextField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ticketing_ticket"
        ordering = ("-created_at",)
        unique_together = (("booking", "passenger", "reissue_parent"),)


class TicketAuditEvent(models.Model):
    pnr_record = models.ForeignKey(PNRRecord, null=True, blank=True, related_name="audit_events", on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, null=True, blank=True, related_name="audit_events", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    status_from = models.CharField(max_length=20, blank=True)
    status_to = models.CharField(max_length=20, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticketing_audit_event"
        ordering = ("-created_at",)
