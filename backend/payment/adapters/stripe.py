import os
from django.conf import settings
from .base import BaseGateway

class StripeGateway(BaseGateway):
    """Stripe gateway stub implementation.

    This implementation uses the `stripe` library if available; otherwise, it raises a NotImplementedError.
    It provides the same interface as RazorpayGateway but does not perform actual calls.
    """

    def __init__(self):
        try:
            import stripe
            self.stripe = stripe
        except ImportError as exc:
            raise ImportError('stripe library is not installed') from exc
        self.stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if not self.stripe.api_key:
            raise ValueError('Stripe secret key not set in environment variables')

    def create_payment_intent(self, amount: int, currency: str, metadata: dict = None) -> dict:
        # Stripe expects amount in the smallest currency unit
        amount_in_subunit = int(amount * 100)
        intent_data = {
            'amount': amount_in_subunit,
            'currency': currency,
            'metadata': metadata or {},
        }
        intent = self.stripe.PaymentIntent.create(**intent_data)
        return intent

    def capture_payment(self, payment_id: str, amount: int = None) -> dict:
        # For Stripe, capture on the PaymentIntent
        capture_params = {}
        if amount is not None:
            capture_params['amount_to_capture'] = int(amount * 100)
        return self.stripe.PaymentIntent.capture(payment_id, **capture_params)

    def refund_payment(self, payment_id: str, amount: int = None) -> dict:
        refund_params = {'payment_intent': payment_id}
        if amount is not None:
            refund_params['amount'] = int(amount * 100)
        return self.stripe.Refund.create(**refund_params)

    def verify_webhook(self, request) -> bool:
        # Stripe sends a signature header "Stripe-Signature"
        signature = request.headers.get('Stripe-Signature')
        if not signature:
            raise ValueError('Missing Stripe signature header')
        payload = request.body.decode('utf-8')
        secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        if not secret:
            raise ValueError('Stripe webhook secret not configured')
        try:
            self.stripe.Webhook.construct_event(payload, signature, secret)
            return True
        except self.stripe.error.SignatureVerificationError as e:
            raise ValueError('Invalid Stripe webhook signature') from e
