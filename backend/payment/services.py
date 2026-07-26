import uuid
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from .models import PaymentTransaction, RefundTransaction
from .adapters.base import get_gateway


def initiate_payment(amount, currency='INR', gateway=None, metadata=None):
    """Create a payment intent and corresponding PaymentTransaction record.
    Returns a dict with provider-specific intent data and the transaction id.
    """
    if metadata is None:
        metadata = {}
    # Choose gateway implementation
    gateway_impl = get_gateway(gateway)
    # Create intent with provider
    provider_intent = gateway_impl.create_payment_intent(amount, currency, metadata)
    # Record transaction in DB
    with transaction.atomic():
        transaction_obj = PaymentTransaction.objects.create(
            id=uuid.uuid4(),
            gateway=gateway_impl.name,
            status=PaymentTransaction.STATUS_CREATED,
            amount=amount,
            currency=currency,
            external_reference=provider_intent.get('id') or provider_intent.get('order_id') or provider_intent.get('intent') or ''
        )
    # Return combined info for API response
    result = {
        'transaction_id': str(transaction_obj.id),
        'gateway': transaction_obj.gateway,
        'status': transaction_obj.status,
        'provider_intent': provider_intent,
    }
    return result


def capture_payment(transaction_id, amount=None):
    """Capture a payment for the given transaction.
    Updates the PaymentTransaction status and returns provider response.
    """
    try:
        payment = PaymentTransaction.objects.select_for_update().get(id=transaction_id)
    except PaymentTransaction.DoesNotExist:
        raise ValueError('Payment transaction not found')
    gateway_impl = get_gateway(payment.gateway)
    provider_response = gateway_impl.capture_payment(payment.external_reference, amount)
    # Update status based on provider response – simple heuristic
    new_status = PaymentTransaction.STATUS_CAPTURED if provider_response else PaymentTransaction.STATUS_FAILED
    payment.status = new_status
    payment.updated_at = timezone.now()
    payment.save(update_fields=['status', 'updated_at'])
    return {'transaction_id': str(payment.id), 'status': payment.status, 'provider_response': provider_response}


def process_refund(transaction_id, amount=None):
    """Process a refund for a captured payment.
    Creates a RefundTransaction record and updates the original payment status if fully refunded.
    """
    try:
        payment = PaymentTransaction.objects.select_for_update().get(id=transaction_id)
    except PaymentTransaction.DoesNotExist:
        raise ValueError('Payment transaction not found')
    if payment.status != PaymentTransaction.STATUS_CAPTURED:
        raise ValueError('Only captured payments can be refunded')
    gateway_impl = get_gateway(payment.gateway)
    provider_response = gateway_impl.refund_payment(payment.external_reference, amount)
    # Record refund transaction
    with transaction.atomic():
        refund = RefundTransaction.objects.create(
            id=uuid.uuid4(),
            payment=payment,
            amount=amount if amount is not None else payment.amount,
            currency=payment.currency,
            status=RefundTransaction.STATUS_CREATED,
            external_reference=provider_response.get('id') or ''
        )
        # Update payment status if full refund
        if amount is None or amount >= payment.amount:
            payment.status = PaymentTransaction.STATUS_REFUNDED
            payment.save(update_fields=['status'])
        # Update refund status based on provider response
        refund.status = RefundTransaction.STATUS_COMPLETED if provider_response else RefundTransaction.STATUS_FAILED
        refund.save(update_fields=['status'])
    return {'refund_id': str(refund.id), 'status': refund.status, 'provider_response': provider_response}
