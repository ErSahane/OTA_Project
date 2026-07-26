from datetime import date

from rest_framework import serializers

from pricing.serializers import PricingQuoteSerializer


class ContactSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=30)


class BookingPassengerSerializer(serializers.Serializer):
    passenger_type = serializers.ChoiceField(choices=("ADT", "CHD", "INF"))
    title = serializers.CharField(max_length=20, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    gender = serializers.CharField(max_length=20, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    ssr_codes = serializers.ListField(child=serializers.CharField(max_length=20), required=False, allow_empty=True, default=list)

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("date_of_birth cannot be in the future.")
        return value


class BookingSessionCreateSerializer(serializers.Serializer):
    provider_name = serializers.CharField(max_length=100)
    search_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    selected_offer = serializers.JSONField()
    pricing_request = PricingQuoteSerializer()
    passengers = BookingPassengerSerializer(many=True)
    contact = ContactSerializer()
    hold_minutes = serializers.IntegerField(min_value=1, max_value=60, default=15)
    idempotency_key = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, attrs):
        adults = sum(1 for item in attrs["passengers"] if item["passenger_type"] == "ADT")
        infants = sum(1 for item in attrs["passengers"] if item["passenger_type"] == "INF")
        if adults < 1:
            raise serializers.ValidationError("At least one adult passenger is required.")
        if infants > adults:
            raise serializers.ValidationError("Infants cannot exceed adult passengers.")
        return attrs


class BookingConfirmSerializer(serializers.Serializer):
    session_token = serializers.CharField(max_length=64)


class BookingSessionResponseSerializer(serializers.Serializer):
    session_token = serializers.CharField()
    booking_token = serializers.CharField()
    status = serializers.CharField()
    provider_name = serializers.CharField()
    quoted_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    hold_expires_at = serializers.DateTimeField()


class BookingPassengerReadSerializer(serializers.Serializer):
    passenger_type = serializers.CharField()
    title = serializers.CharField(allow_blank=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.CharField(allow_blank=True)
    date_of_birth = serializers.DateField(allow_null=True)
    ssr_requests = serializers.ListField(child=serializers.CharField())


class BookingReadSerializer(serializers.Serializer):
    reference = serializers.CharField()
    provider_name = serializers.CharField()
    provider_booking_reference = serializers.CharField(allow_blank=True)
    currency = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField()
    contact_first_name = serializers.CharField()
    contact_last_name = serializers.CharField()
    passengers = BookingPassengerReadSerializer(many=True)


class BookingStatusSerializer(serializers.Serializer):
    reference = serializers.CharField()
    status = serializers.CharField()
