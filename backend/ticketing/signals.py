from django.dispatch import Signal

# Signals for Ticketing and PNR Engine Events
ticket_issued = Signal()  # providing_args=["ticket", "booking"]
ticket_voided = Signal()  # providing_args=["ticket", "booking"]
ticket_reissued = Signal()  # providing_args=["old_ticket", "new_ticket", "booking"]
pnr_synced = Signal()  # providing_args=["pnr_record", "booking"]
