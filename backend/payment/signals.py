from django.dispatch import Signal

# Signals for payment workflow events
payment_initiated = Signal()
payment_captured = Signal()
payment_refunded = Signal()
payment_failed = Signal()
