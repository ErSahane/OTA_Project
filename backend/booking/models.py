import uuid

from django.conf import settings
from django.db import models


class BookingSession(models.Model):
    STATUS_INITIATED = "initiated"
    STATUS_REVALIDATED = "revalidated"
    STATUS_HELD = "held"
    STATUS_BOOKED = "booked"
    STATUS_FAILED = "failed"
    STATUS_EXPIRED = "expired"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_INITIATED, "Initiated"),
        (STATUS_REVALIDATED, "Revalidated"),
        (STATUS_HELD, "Held"),
        (STATUS_BOOKED, "Booked"),
        (STATUS_FAILED, "Failed"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="booking_sessions", null=True, blank=True, on_delete=models.SET_NULL)
    session_token = models.CharField(max_length=64, unique=True)
    booking_token = models.CharField(max_length=64, unique=True)
    idempotency_key = models.CharField(max_length=100, unique=True)
    provider_name = models.CharField(max_length=100)
    search_reference = models.CharField(max_length=100, blank=True)
    selected_offer = models.JSONField(default=dict, blank=True)
    pricing_request = models.JSONField(default=dict, blank=True)
    quoted_total = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INITIATED)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=30)
    contact_first_name = models.CharField(max_length=150)
    contact_last_name = models.CharField(max_length=150)
    correlation_id = models.CharField(max_length=100, blank=True)
    provider_hold_reference = models.CharField(max_length=100, blank=True)
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "booking_session"
        ordering = ("-created_at",)


class Booking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_HELD = "held"
    STATUS_CONFIRMED = "confirmed"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_HELD, "Held"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(BookingSession, related_name="booking", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bookings", null=True, blank=True, on_delete=models.SET_NULL)
    reference = models.CharField(max_length=32, unique=True)
    provider_name = models.CharField(max_length=100)
    provider_booking_reference = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=30)
    contact_first_name = models.CharField(max_length=150)
    contact_last_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "booking"
        ordering = ("-created_at",)


class BookingPassenger(models.Model):
    booking = models.ForeignKey(Booking, related_name="passengers", on_delete=models.CASCADE)
    passenger_type = models.CharField(max_length=10)
    title = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    ssr_requests = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "booking_passenger"


class BookingAuditEvent(models.Model):
    session = models.ForeignKey(BookingSession, null=True, blank=True, related_name="audit_events", on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, null=True, blank=True, related_name="audit_events", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    state_from = models.CharField(max_length=20, blank=True)
    state_to = models.CharField(max_length=20, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "booking_audit_event"
        ordering = ("-created_at",)
