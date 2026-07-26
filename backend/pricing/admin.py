from django.contrib import admin

from .models import FarePolicy, PricingAdjustment

admin.site.register(FarePolicy)
admin.site.register(PricingAdjustment)
