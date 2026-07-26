from django.dispatch import Signal

# Fired when a cancellation request is first initiated
cancellation_initiated = Signal()  # providing_args=["cancellation_request", "booking"]

# Fired when a cancellation is approved and processed with GDS
cancellation_approved = Signal()  # providing_args=["cancellation_request", "refund_claim", "booking"]

# Fired when a cancellation request is rejected
cancellation_rejected = Signal()  # providing_args=["cancellation_request", "booking"]

# Fired when a refund claim transitions to settled
refund_settled = Signal()  # providing_args=["refund_claim", "booking"]
