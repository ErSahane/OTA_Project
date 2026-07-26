from django.db import models


class FarePolicy(models.Model):
    code = models.CharField(max_length=50, unique=True)
    fare_family = models.CharField(max_length=100)
    fare_basis = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=3)
    refundable = models.BooleanField(default=False)
    cancellation_allowed = models.BooleanField(default=False)
    date_change_allowed = models.BooleanField(default=False)
    cancellation_penalty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_change_penalty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    baggage_rules = models.JSONField(default=dict, blank=True)
    refund_rules = models.JSONField(default=dict, blank=True)
    ancillary_rules = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pricing_fare_policy"


class PricingAdjustment(models.Model):
    TAX = "tax"
    MARKUP = "markup"
    SERVICE_FEE = "service_fee"
    DISCOUNT = "discount"
    PROMO = "promo"
    TYPES = ((TAX, "Tax"), (MARKUP, "Markup"), (SERVICE_FEE, "Service fee"), (DISCOUNT, "Discount"), (PROMO, "Promo"))
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    AMOUNT_TYPES = ((PERCENTAGE, "Percentage"), (FIXED, "Fixed"))

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    adjustment_type = models.CharField(max_length=20, choices=TYPES)
    amount_type = models.CharField(max_length=20, choices=AMOUNT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=4)
    currency = models.CharField(max_length=3, blank=True)
    promo_code = models.CharField(max_length=50, blank=True)
    priority = models.PositiveIntegerField(default=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pricing_adjustment"
        ordering = ("priority", "code")
