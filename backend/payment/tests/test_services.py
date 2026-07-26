import uuid
from unittest import mock
from django.test import TestCase
from payment.services import initiate_payment, capture_payment, process_refund
from payment.models import PaymentTransaction, RefundTransaction

class InitiatePaymentServiceTest(TestCase):
    def setUp(self):
        self.mock_gateway = mock.Mock()
        self.mock_gateway.name = 'razorpay'
        self.mock_gateway.create_payment_intent.return_value = {'id': 'order_123'}
        self.patcher = mock.patch('payment.services.get_gateway', return_value=self.mock_gateway)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_initiate_payment_creates_transaction(self):
        result = initiate_payment(amount=1000, currency='INR', gateway='razorpay', metadata={'receipt': 'rcpt_1'})
        self.assertEqual(result['gateway'], 'razorpay')
        self.assertEqual(result['status'], PaymentTransaction.STATUS_CREATED)
        self.assertTrue(PaymentTransaction.objects.filter(external_reference='order_123').exists())
        self.mock_gateway.create_payment_intent.assert_called_once()

class CapturePaymentServiceTest(TestCase):
    def setUp(self):
        self.tx = PaymentTransaction.objects.create(
            id=uuid.uuid4(),
            gateway=PaymentTransaction.GATEWAY_RAZORPAY,
            status=PaymentTransaction.STATUS_CREATED,
            amount=1000,
            currency='INR',
            external_reference='order_123'
        )
        self.mock_gateway = mock.Mock()
        self.mock_gateway.name = 'razorpay'
        self.mock_gateway.capture_payment.return_value = {'captured': True}
        self.patcher = mock.patch('payment.services.get_gateway', return_value=self.mock_gateway)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_capture_updates_status(self):
        result = capture_payment(transaction_id=self.tx.id, amount=1000)
        self.assertEqual(result['status'], PaymentTransaction.STATUS_CAPTURED)
        self.tx.refresh_from_db()
        self.assertEqual(self.tx.status, PaymentTransaction.STATUS_CAPTURED)
        self.mock_gateway.capture_payment.assert_called_once()

class RefundServiceTest(TestCase):
    def setUp(self):
        self.tx = PaymentTransaction.objects.create(
            id=uuid.uuid4(),
            gateway=PaymentTransaction.GATEWAY_RAZORPAY,
            status=PaymentTransaction.STATUS_CAPTURED,
            amount=1000,
            currency='INR',
            external_reference='order_123'
        )
        self.mock_gateway = mock.Mock()
        self.mock_gateway.name = 'razorpay'
        self.mock_gateway.refund_payment.return_value = {'id': 'refund_456'}
        self.patcher = mock.patch('payment.services.get_gateway', return_value=self.mock_gateway)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_refund_creates_refund_record(self):
        result = process_refund(transaction_id=self.tx.id, amount=200)
        self.assertEqual(result['status'], RefundTransaction.STATUS_COMPLETED)
        self.assertTrue(RefundTransaction.objects.filter(external_reference='refund_456').exists())
        self.mock_gateway.refund_payment.assert_called_once()
