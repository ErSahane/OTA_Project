from datetime import date
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from master_data.models import Airport, CabinClass, City
from .models import FlightSearchQuery, FlightSearchSegment

TRIP_TYPES = ("one-way", "round-trip", "multi-city")
MAX_PASSENGERS = 9


class FlightSearchSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightSearchSegment
        fields = ("origin", "destination", "departure_date", "return_date")

    @staticmethod
    def _location(value, field):
        code = value.strip().upper()
        if not (Airport.objects.filter(code=code, is_deleted=False).exists() or City.objects.filter(code=code, is_deleted=False).exists()):
            raise serializers.ValidationError(f"Invalid {field} code: {value}.")
        return code

    def validate_origin(self, value):
        return self._location(value, "origin")

    def validate_destination(self, value):
        return self._location(value, "destination")

    def validate_departure_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Departure date cannot be in the past.")
        return value

    def validate(self, attrs):
        if attrs["origin"] == attrs["destination"]:
            raise serializers.ValidationError("Origin and destination must be different.")
        return attrs


class FlightSearchHistorySerializer(serializers.ModelSerializer):
    segments = FlightSearchSegmentSerializer(many=True, read_only=True)

    class Meta:
        model = FlightSearchQuery
        fields = ("id", "trip_type", "cabin_class", "passenger_adults", "passenger_children", "passenger_infants", "segments", "created_at")


class FlightSearchQuerySerializer(serializers.ModelSerializer):
    segments = FlightSearchSegmentSerializer(many=True)

    class Meta:
        model = FlightSearchQuery
        fields = ("trip_type", "cabin_class", "passenger_adults", "passenger_children", "passenger_infants", "segments")
        extra_kwargs = {"passenger_adults": {"min_value": 1}, "passenger_children": {"min_value": 0}, "passenger_infants": {"min_value": 0}}

    def validate_trip_type(self, value):
        value = value.strip().lower()
        if value not in TRIP_TYPES:
            raise serializers.ValidationError(f"trip_type must be one of: {', '.join(TRIP_TYPES)}.")
        return value

    def validate_cabin_class(self, value):
        value = value.strip().upper()
        if not CabinClass.objects.filter(code=value, is_deleted=False).exists():
            raise serializers.ValidationError("Invalid cabin class.")
        return value

    def validate(self, attrs):
        adults, children, infants = attrs["passenger_adults"], attrs.get("passenger_children", 0), attrs.get("passenger_infants", 0)
        segments, trip_type = attrs["segments"], attrs["trip_type"]
        if adults + children + infants > MAX_PASSENGERS:
            raise serializers.ValidationError(f"A search supports at most {MAX_PASSENGERS} passengers.")
        if infants > adults:
            raise serializers.ValidationError("Number of infants cannot exceed the number of adults.")
        if trip_type == "one-way":
            if len(segments) != 1 or segments[0].get("return_date"):
                raise serializers.ValidationError("One-way search requires exactly one segment and no return date.")
        elif trip_type == "round-trip":
            if len(segments) != 1 or not segments[0].get("return_date"):
                raise serializers.ValidationError("Round-trip search requires one segment and a return date.")
            if segments[0]["return_date"] < segments[0]["departure_date"]:
                raise serializers.ValidationError("Return date cannot precede departure date.")
        else:
            if len(segments) < 2:
                raise serializers.ValidationError("Multi-city search must contain at least two segments.")
            previous = None
            for segment in segments:
                if segment.get("return_date") or (previous and segment["departure_date"] < previous):
                    raise serializers.ValidationError("Multi-city segments cannot have return dates and must be chronological.")
                previous = segment["departure_date"]
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        segments = validated_data.pop("segments")
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        query = FlightSearchQuery.objects.create(user=user, **validated_data)
        FlightSearchSegment.objects.bulk_create([FlightSearchSegment(query=query, sequence=index, **segment) for index, segment in enumerate(segments)])
        return query

class FlightSearchOptionsSerializer(serializers.Serializer):
    providers = serializers.ListField(child=serializers.CharField(max_length=100), required=False)
    airlines = serializers.ListField(child=serializers.CharField(max_length=10), required=False)
    min_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"), required=False)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0"), required=False)
    max_stops = serializers.IntegerField(min_value=0, max_value=5, required=False)
    sort = serializers.ChoiceField(choices=("price", "-price", "duration", "-duration", "stops", "-stops"), default="price")
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)

    def validate(self, attrs):
        if attrs.get("min_price") is not None and attrs.get("max_price") is not None and attrs["min_price"] > attrs["max_price"]:
            raise serializers.ValidationError("min_price cannot exceed max_price.")
        return attrs
