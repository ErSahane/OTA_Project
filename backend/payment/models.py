import uuid
from django.db import models
from django.conf import settings

class PaymentTransaction(models.Model):
    STATUS_CREATED = "created"
    STATUS_AUTHORIZED = "authorized"
    STATUS_CAPTURED = "captured"
    STATUS_FAILED = "failed"
    STATUS_REFUNDED = "refunded"
    STATUS_CHOICES = (
        (STATUS_CREATED, "Created"),
        (STATUS_AUTHORIZED, "Authorized"),
        (STATUS_CAPTURED, "Captured"),
        (STATUS_FAILED, "Failed"),
        (STATUS_REFUNDED, "Refunded"),
    )

    GATEWAY_RAZORPAY = "razorpay"
    GATEWAY_STRIPE = "stripe"
    GATEWAY_CHOICES = (
        (GATEWAY_RAZORPAY, "Razorpay"),
        (GATEWAY_STRIPE, "Stripe"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    external_reference = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_transaction"
        ordering = ("-created_at",)

    def __str__(self):
        return f"PaymentTransaction({self.id}, {self.gateway}, {self.amount}{self.currency}, {self.status})"

class RefundTransaction(models.Model):
    STATUS_CREATED = "created"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_CREATED, "Created"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(PaymentTransaction, on_delete=models.PROTECT, related_name="refunds")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    external_reference = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "refund_transaction"
        ordering = ("-created_at",)

    def __str__(self):
        return f"RefundTransaction({self.id}, {self.amount}{self.currency}, {self.status})"


class ProcessedWebhook(models.Model):
    """Store processed webhook events to ensure idempotency."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=20)
    event_id = models.CharField(max_length=150, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "processed_webhook"
        ordering = ("-received_at",)

    def __str__(self):
        return f"ProcessedWebhook({self.provider}, {self.event_id})"
