from django.contrib import admin

from .models import Booking, BookingAuditEvent, BookingPassenger, BookingSession

admin.site.register(BookingSession)
admin.site.register(Booking)
admin.site.register(BookingPassenger)
admin.site.register(BookingAuditEvent)
