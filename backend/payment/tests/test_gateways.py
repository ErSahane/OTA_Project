import os
from unittest import mock
from django.test import TestCase
from payment.adapters.base import get_gateway
from payment.adapters.razorpay import RazorpayGateway

class GatewayFactoryTest(TestCase):
    def test_default_gateway(self):
        # No explicit name, should fall back to settings default (razorpay)
        with mock.patch.dict(os.environ, {'PAYMENT_DEFAULT_GATEWAY': ''}):
            gateway = get_gateway()
            self.assertIsInstance(gateway, RazorpayGateway)

    def test_named_gateway(self):
        gateway = get_gateway('razorpay')
        self.assertIsInstance(gateway, RazorpayGateway)
