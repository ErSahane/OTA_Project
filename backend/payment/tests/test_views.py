from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from unittest import mock
from uuid import uuid4
from payment.models import PaymentTransaction, RefundTransaction

class MockGateway:
    name = 'razorpay'
    def create_payment_intent(self, amount, currency, metadata=None):
        return {'id': 'order_123', 'amount': amount, 'currency': currency}
    def capture_payment(self, payment_id, amount=None):
        return {'captured': True}
    def refund_payment(self, payment_id, amount=None):
        return {'id': 'refund_456'}
    def verify_webhook(self, request):
        return True

class PaymentViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        patcher = mock.patch('payment.services.get_gateway', return_value=MockGateway())
        self.mock_get_gateway = patcher.start()
        self.addCleanup(patcher.stop)

    def test_create_intent(self):
        url = reverse('payment-intent-list')
        data = {'amount': '1000.00', 'currency': 'INR', 'metadata': {'receipt': 'rcpt_1'}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('transaction_id', response.data)
        self.assertTrue(PaymentTransaction.objects.filter(external_reference='order_123').exists())

    def test_capture_payment(self):
        # create transaction first
        pt = PaymentTransaction.objects.create(
            id=uuid4(),
            gateway=PaymentTransaction.GATEWAY_RAZORPAY,
            status=PaymentTransaction.STATUS_CREATED,
            amount=1000,
            currency='INR',
            external_reference='order_123'
        )
        url = reverse('payment-capture-list')
        data = {'transaction_id': str(pt.id), 'amount': '1000.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        pt.refresh_from_db()
        self.assertEqual(pt.status, PaymentTransaction.STATUS_CAPTURED)

    def test_refund_payment(self):
        pt = PaymentTransaction.objects.create(
            id=uuid4(),
            gateway=PaymentTransaction.GATEWAY_RAZORPAY,
            status=PaymentTransaction.STATUS_CAPTURED,
            amount=1000,
            currency='INR',
            external_reference='order_123'
        )
        url = reverse('payment-refund-list')
        data = {'transaction_id': str(pt.id), 'amount': '200.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RefundTransaction.objects.filter(external_reference='refund_456').exists())

    def test_webhook_success(self):
        url = reverse('payment-webhook')
        # mock request headers via client post with HTTP_ prefix
        response = self.client.post(url, {}, format='json', HTTP_X_RAZORPAY_SIGNATURE='validsig')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('status'), 'ok')
