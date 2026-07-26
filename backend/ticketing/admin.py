from django.contrib import admin

from .models import PNRRecord, Ticket, TicketAuditEvent

admin.site.register(PNRRecord)
admin.site.register(Ticket)
admin.site.register(TicketAuditEvent)
