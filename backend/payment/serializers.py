from rest_framework import serializers
from .models import PaymentTransaction, RefundTransaction

class PaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='INR')
    gateway = serializers.CharField(max_length=20, required=False, allow_blank=True)
    metadata = serializers.DictField(child=serializers.CharField(), required=False)

    def create(self, validated_data):
        # Service layer will handle creation
        from .services import initiate_payment
        return initiate_payment(**validated_data)

class PaymentCaptureSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)

    def create(self, validated_data):
        from .services import capture_payment
        return capture_payment(**validated_data)

class RefundSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)

    def create(self, validated_data):
        from .services import process_refund
        return process_refund(**validated_data)

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ('id', 'gateway', 'status', 'amount', 'currency', 'external_reference', 'created_at', 'updated_at')

class RefundTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundTransaction
        fields = ('id', 'payment', 'amount', 'currency', 'status', 'external_reference', 'created_at', 'updated_at')
