from rest_framework import serializers

from .models import PNRRecord, Ticket, TicketAuditEvent


class TicketSerializer(serializers.ModelSerializer):
    passenger_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "booking",
            "passenger",
            "passenger_name",
            "pnr_record",
            "ticket_number",
            "provider_ticket_number",
            "status",
            "coupon_data",
            "reissue_parent",
            "pdf_content",
            "issued_at",
            "voided_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_passenger_name(self, obj) -> str:
        return f"{obj.passenger.first_name} {obj.passenger.last_name}"


class PNRRecordSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source="booking.reference", read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = PNRRecord
        fields = [
            "id",
            "booking",
            "booking_reference",
            "internal_reference",
            "provider_name",
            "provider_pnr",
            "status",
            "synced_at",
            "itinerary_data",
            "invoice_data",
            "tickets",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TicketIssueRequestSerializer(serializers.Serializer):
    booking_reference = serializers.CharField(max_length=32, help_text="The internal booking reference (e.g. BKG...)")
    idempotency_key = serializers.CharField(max_length=100, help_text="Unique key to prevent duplicate ticketing requests")


class TicketReissueRequestSerializer(serializers.Serializer):
    new_pricing = serializers.JSONField(required=True, help_text="New pricing and segment details for the reissue")
    idempotency_key = serializers.CharField(max_length=100, help_text="Unique key for the reissue operation")


class TicketVoidResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    ticket_number = serializers.CharField()
    status = serializers.CharField()


class TicketAuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAuditEvent
        fields = "__all__"
