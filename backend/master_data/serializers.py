from rest_framework import serializers

from .models import (
    Airline,
    Airport,
    CabinClass,
    City,
    Country,
    Currency,
    FareType,
    Language,
    PassengerType,
    StateRegion,
    TripType,
)


class BaseMasterSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return super().create(validated_data)


class CountrySerializer(BaseMasterSerializer):
    class Meta:
        model = Country
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]


class StateRegionSerializer(BaseMasterSerializer):
    class Meta:
        model = StateRegion
        fields = ["id", "country", "code", "name", "created_at", "updated_at", "is_deleted"]


class CitySerializer(BaseMasterSerializer):
    class Meta:
        model = City
        fields = ["id", "state", "code", "name", "created_at", "updated_at", "is_deleted"]


class AirportSerializer(BaseMasterSerializer):
    class Meta:
        model = Airport
        fields = ["id", "city", "code", "name", "created_at", "updated_at", "is_deleted"]


class AirlineSerializer(BaseMasterSerializer):
    class Meta:
        model = Airline
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]


class CurrencySerializer(BaseMasterSerializer):
    class Meta:
        model = Currency
        fields = ["id", "code", "name", "symbol", "created_at", "updated_at", "is_deleted"]


class LanguageSerializer(BaseMasterSerializer):
    class Meta:
        model = Language
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]


class CabinClassSerializer(BaseMasterSerializer):
    class Meta:
        model = CabinClass
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]


class PassengerTypeSerializer(BaseMasterSerializer):
    class Meta:
        model = PassengerType
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]


class TripTypeSerializer(BaseMasterSerializer):
    class Meta:
        model = TripType
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]


class FareTypeSerializer(BaseMasterSerializer):
    class Meta:
        model = FareType
        fields = ["id", "code", "name", "created_at", "updated_at", "is_deleted"]
