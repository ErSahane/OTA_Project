import abc
from typing import Any, Dict

class BaseGateway(abc.ABC):
    """Abstract base class for payment gateway adapters.

    Implementations must provide methods for creating payment intents,
    capturing payments, processing refunds, and verifying webhooks.
    """

    @abc.abstractmethod
    def create_payment_intent(self, amount: int, currency: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a payment intent/order with the provider.
        Returns a dict containing provider-specific data (e.g., order_id).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def capture_payment(self, payment_id: str, amount: int = None) -> Dict[str, Any]:
        """Capture a previously created payment.
        Returns provider response.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refund_payment(self, payment_id: str, amount: int = None) -> Dict[str, Any]:
        """Refund a captured payment.
        Returns provider response.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify_webhook(self, request) -> bool:
        """Verify the authenticity of a webhook request.
        Should raise an exception on failure.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Return a short identifier for the gateway (e.g., 'razorpay')."""
        return self.__class__.__name__.replace('Gateway', '').lower()

def get_gateway(name: str = None):
    """Factory to obtain a gateway instance.
    If *name* is None, uses the default gateway from settings.
    """
    from django.conf import settings
    from importlib import import_module

    if not name:
        name = getattr(settings, 'PAYMENT_DEFAULT_GATEWAY', 'razorpay')
    name = name.lower()
    if name == 'razorpay':
        module = import_module('payment.adapters.razorpay')
        return module.RazorpayGateway()
    elif name == 'stripe':
        module = import_module('payment.adapters.stripe')
        return module.StripeGateway()
    else:
        raise ValueError(f"Unsupported payment gateway: {name}")
