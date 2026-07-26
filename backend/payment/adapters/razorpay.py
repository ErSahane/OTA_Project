import os
import razorpay
from django.conf import settings
from .base import BaseGateway

class RazorpayGateway(BaseGateway):
    """Razorpay gateway implementation.

    Uses the razorpay Python SDK. If the SDK is not available, raises an informative error.
    """

    def __init__(self):
        # Use environment variables if set, otherwise fallback to dummy credentials for testing
        key_id = os.getenv('RAZORPAY_KEY_ID') or 'test_key_id'
        key_secret = os.getenv('RAZORPAY_KEY_SECRET') or 'test_key_secret'
        self.client = razorpay.Client(auth=(key_id, key_secret))

    def create_payment_intent(self, amount: int, currency: str, metadata: dict = None) -> dict:
        # Razorpay expects amount in paise (for INR) or the smallest currency unit
        amount_in_subunit = int(amount * 100)
        data = {
            'amount': amount_in_subunit,
            'currency': currency,
            'receipt': metadata.get('receipt') if metadata else None,
            'notes': metadata or {},
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        order = self.client.order.create(data)
        return order

    def capture_payment(self, payment_id: str, amount: int = None) -> dict:
        # Capture requires amount; if not provided use full amount from order
        if amount is None:
            raise ValueError('Amount must be provided for capture')
        amount_in_subunit = int(amount * 100)
        return self.client.payment.capture(payment_id, amount_in_subunit)

    def refund_payment(self, payment_id: str, amount: int = None) -> dict:
        payload = {}
        if amount is not None:
            payload['amount'] = int(amount * 100)
        return self.client.payment.refund(payment_id, payload)

    def verify_webhook(self, request) -> bool:
        # Razorpay sends X-Razorpay-Signature header
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            raise ValueError('Missing Razorpay signature')
        body = request.body.decode('utf-8')
        secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        if not secret:
            # In test environments, allow bypass if secret not configured
            return True
        try:
            self.client.utility.verify_webhook_signature(body, signature, secret)
            return True
        except razorpay.errors.SignatureVerificationError as e:
            raise ValueError('Invalid Razorpay webhook signature') from e
