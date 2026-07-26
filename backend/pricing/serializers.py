from decimal import Decimal

from rest_framework import serializers


class PricingPassengerSerializer(serializers.Serializer):
    passenger_type = serializers.CharField(max_length=10)
    quantity = serializers.IntegerField(min_value=1, max_value=9)


class PriceLineSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, required=False)
    name = serializers.CharField(max_length=100, required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"))
    quantity = serializers.IntegerField(min_value=1, default=1)


class PricingQuoteSerializer(serializers.Serializer):
    currency = serializers.CharField(min_length=3, max_length=3)
    base_fare = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"))
    passengers = PricingPassengerSerializer(many=True)
    taxes = PriceLineSerializer(many=True, required=False, default=list)
    ancillaries = PriceLineSerializer(many=True, required=False, default=list)
    seats = PriceLineSerializer(many=True, required=False, default=list)
    fare_policy_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    promo_code = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, attrs):
        if sum(item["quantity"] for item in attrs["passengers"]) > 9:
            raise serializers.ValidationError("A quote supports at most 9 passengers.")
        attrs["currency"] = attrs["currency"].upper()
        return attrs
