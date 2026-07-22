from datetime import date
from rest_framework import serializers

from master_data.models import Airport, CabinClass, City
from .models import FlightSearchQuery, FlightSearchSegment


class FlightSearchSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightSearchSegment
        fields = ["origin", "destination", "departure_date", "return_date"]

    def validate_origin(self, value):
        val = value.upper()
        if not (Airport.objects.filter(code=val, is_deleted=False).exists() or 
                City.objects.filter(code=val, is_deleted=False).exists()):
            raise serializers.ValidationError(f"Invalid origin code: {value}. Must be a valid airport or city.")
        return val

    def validate_destination(self, value):
        val = value.upper()
        if not (Airport.objects.filter(code=val, is_deleted=False).exists() or 
                City.objects.filter(code=val, is_deleted=False).exists()):
            raise serializers.ValidationError(f"Invalid destination code: {value}. Must be a valid airport or city.")
        return val

    def validate_departure_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Departure date cannot be in the past.")
        return value


class FlightSearchQuerySerializer(serializers.ModelSerializer):
    segments = FlightSearchSegmentSerializer(many=True)

    class Meta:
        model = FlightSearchQuery
        fields = ["trip_type", "cabin_class", "passenger_adults", "passenger_children", "passenger_infants", "segments"]

    def validate_trip_type(self, value):
        choices = ["one-way", "round-trip", "multi-city"]
        if value.lower() not in choices:
            raise serializers.ValidationError(f"Invalid trip_type: {value}. Choices are {choices}")
        return value.lower()

    def validate_cabin_class(self, value):
        val = value.upper()
        if not CabinClass.objects.filter(code=val, is_deleted=False).exists():
            raise serializers.ValidationError(f"Invalid cabin class: {value}. Must exist in master data CabinClass.")
        return val

    def validate(self, data):
        adults = data.get("passenger_adults", 1)
        infants = data.get("passenger_infants", 0)

        if adults < 1:
            raise serializers.ValidationError("At least 1 adult passenger is required.")
        if infants > adults:
            raise serializers.ValidationError("Number of infants cannot exceed the number of adults.")

        trip_type = data.get("trip_type")
        segments = data.get("segments", [])

        if not segments:
            raise serializers.ValidationError("At least one travel segment is required.")

        if trip_type == "one-way":
            if len(segments) != 1:
                raise serializers.ValidationError("One-way search must have exactly 1 segment.")
        elif trip_type == "round-trip":
            if len(segments) != 1:
                raise serializers.ValidationError("Round-trip search must have exactly 1 segment.")
            seg = segments[0]
            ret_date = seg.get("return_date")
            dep_date = seg.get("departure_date")
            if not ret_date:
                raise serializers.ValidationError("Return date is required for round-trip search.")
            if ret_date < dep_date:
                raise serializers.ValidationError("Return date must be equal to or after the departure date.")
        elif trip_type == "multi-city":
            if len(segments) < 2:
                raise serializers.ValidationError("Multi-city search must have at least 2 segments.")
            for i in range(len(segments) - 1):
                if segments[i+1]["departure_date"] < segments[i]["departure_date"]:
                    raise serializers.ValidationError(
                        f"Segment {i+2} departure date cannot be before segment {i+1} departure date."
                    )

        return data

    def create(self, validated_data):
        segments_data = validated_data.pop("segments")
        user = self.context.get("request").user if "request" in self.context else None
        if user and not user.is_authenticated:
            user = None

        query = FlightSearchQuery.objects.create(user=user, **validated_data)
        for idx, seg_data in enumerate(segments_data):
            FlightSearchSegment.objects.create(query=query, sequence=idx, **seg_data)
        return query
