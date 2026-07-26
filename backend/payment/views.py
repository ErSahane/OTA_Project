from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import (
    PaymentIntentSerializer,
    PaymentCaptureSerializer,
    RefundSerializer,
    PaymentTransactionSerializer,
    RefundTransactionSerializer,
)
from .models import PaymentTransaction, RefundTransaction
from .services import initiate_payment, capture_payment, process_refund
from .signals import payment_initiated, payment_captured, payment_refunded, payment_failed

class PaymentIntentViewSet(viewsets.ViewSet):
    """Create a payment intent/order (unified API)."""

    def create(self, request):
        serializer = PaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        # Emit signal
        payment_initiated.send(sender=self.__class__, transaction_id=result['transaction_id'])
        return Response(result, status=status.HTTP_201_CREATED)

class PaymentCaptureViewSet(viewsets.ViewSet):
    """Capture a previously created payment."""

    def create(self, request):
        serializer = PaymentCaptureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        payment_captured.send(sender=self.__class__, transaction_id=result['transaction_id'])
        return Response(result, status=status.HTTP_200_OK)

class RefundViewSet(viewsets.ViewSet):
    """Process a refund for a captured payment."""

    def create(self, request):
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        payment_refunded.send(sender=self.__class__, refund_id=result['refund_id'])
        return Response(result, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def webhook_view(request):
    """Unified webhook endpoint for all payment providers.
    Determines provider by inspecting headers.
    """
    # Identify provider
    if 'X-Razorpay-Signature' in request.headers:
        provider = 'razorpay'
    elif 'Stripe-Signature' in request.headers:
        provider = 'stripe'
    else:
        return Response({'detail': 'Unsupported provider'}, status=status.HTTP_400_BAD_REQUEST)
    from .adapters.base import get_gateway
    gateway = get_gateway(provider)
    try:
        gateway.verify_webhook(request)
    except Exception as exc:
        payment_failed.send(sender='webhook', provider=provider, error=str(exc))
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    # Process payload (simplified – real implementation would map event types)
    payload = request.data
    # Idempotent handling – store processed event IDs in cache (omitted for brevity)
    # Here we just acknowledge
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)
