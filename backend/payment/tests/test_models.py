from django.test import TestCase
from django.utils import timezone
from payment.models import PaymentTransaction, RefundTransaction, ProcessedWebhook
import uuid

class PaymentTransactionModelTest(TestCase):
    def test_creation_and_str(self):
        pt = PaymentTransaction.objects.create(
            id=uuid.uuid4(),
            gateway=PaymentTransaction.GATEWAY_RAZORPAY,
            status=PaymentTransaction.STATUS_CREATED,
            amount=1000.00,
            currency='INR',
            external_reference='ref123'
        )
        self.assertEqual(pt.gateway, PaymentTransaction.GATEWAY_RAZORPAY)
        self.assertIn('PaymentTransaction', str(pt))

class RefundTransactionModelTest(TestCase):
    def test_refund_creation_and_str(self):
        pt = PaymentTransaction.objects.create(
            id=uuid.uuid4(),
            gateway=PaymentTransaction.GATEWAY_RAZORPAY,
            status=PaymentTransaction.STATUS_CAPTURED,
            amount=1000.00,
            currency='INR',
            external_reference='ref123'
        )
        rt = RefundTransaction.objects.create(
            id=uuid.uuid4(),
            payment=pt,
            amount=200.00,
            currency='INR',
            external_reference='refrefund'
        )
        self.assertEqual(rt.payment, pt)
        self.assertIn('RefundTransaction', str(rt))

class ProcessedWebhookModelTest(TestCase):
    def test_unique_event_id(self):
        ProcessedWebhook.objects.create(provider='razorpay', event_id='evt_1')
        with self.assertRaises(Exception):
            # Django raises IntegrityError on duplicate unique field
            ProcessedWebhook.objects.create(provider='razorpay', event_id='evt_1')
