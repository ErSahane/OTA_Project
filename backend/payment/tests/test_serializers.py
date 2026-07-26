from django.test import TestCase
from payment.serializers import PaymentIntentSerializer, PaymentCaptureSerializer, RefundSerializer

class PaymentIntentSerializerTest(TestCase):
    def test_valid_data(self):
        data = {'amount': '1000.00', 'currency': 'INR', 'gateway': 'razorpay', 'metadata': {'receipt': 'rcpt_1'}}
        serializer = PaymentIntentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        # create method will call service; we can mock it

class PaymentCaptureSerializerTest(TestCase):
    def test_valid_data(self):
        data = {'transaction_id': '11111111-1111-1111-1111-111111111111', 'amount': '500.00'}
        serializer = PaymentCaptureSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class RefundSerializerTest(TestCase):
    def test_valid_data(self):
        data = {'transaction_id': '11111111-1111-1111-1111-111111111111', 'amount': '200.00'}
        serializer = RefundSerializer(data=data)
        self.assertTrue(serializer.is_valid())
