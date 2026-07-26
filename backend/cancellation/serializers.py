from rest_framework import serializers

from .models import CancellationAuditEvent, CancellationRequest, RefundClaim, RefundLedgerEntry


class CancellationInitiateSerializer(serializers.Serializer):
    booking_reference = serializers.CharField(
        max_length=32,
        help_text="Internal booking reference (e.g. BKGxxxxxxxx).",
    )
    cancellation_type = serializers.ChoiceField(
        choices=CancellationRequest.CANCELLATION_TYPES,
        default=CancellationRequest.TYPE_FULL,
    )
    passenger_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        default=list,
        help_text="Passenger UUIDs to cancel (required for partial_passengers type).",
    )
    segment_indexes = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=False,
        allow_empty=True,
        default=list,
        help_text="Segment indexes to cancel (required for partial_segments type).",
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Customer or agent reason for cancellation.",
    )
    idempotency_key = serializers.CharField(
        max_length=128,
        help_text="Unique key for safe duplicate request handling.",
    )

    def validate(self, attrs):
        ctype = attrs.get("cancellation_type")
        if ctype == CancellationRequest.TYPE_PARTIAL_PASSENGERS and not attrs.get("passenger_ids"):
            raise serializers.ValidationError(
                "passenger_ids is required for partial_passengers cancellation type."
            )
        if ctype == CancellationRequest.TYPE_PARTIAL_SEGMENTS and not attrs.get("segment_indexes"):
            raise serializers.ValidationError(
                "segment_indexes is required for partial_segments cancellation type."
            )
        return attrs


class CancellationApproveSerializer(serializers.Serializer):
    """Empty body – approval is action-based."""
    pass


class CancellationRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Reason for rejecting the cancellation request.",
    )


class RefundLedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundLedgerEntry
        fields = ["id", "entry_type", "amount", "currency", "description", "created_at"]
        read_only_fields = fields


class RefundClaimSerializer(serializers.ModelSerializer):
    ledger_entries = RefundLedgerEntrySerializer(many=True, read_only=True)
    booking_reference = serializers.CharField(source="booking.reference", read_only=True)

    class Meta:
        model = RefundClaim
        fields = [
            "id",
            "booking",
            "booking_reference",
            "cancellation_request",
            "currency",
            "gross_fare",
            "airline_penalty",
            "ota_fee",
            "net_refund",
            "status",
            "refund_method",
            "gateway_reference",
            "settled_at",
            "notes",
            "ledger_entries",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CancellationRequestSerializer(serializers.ModelSerializer):
    refund_claim = RefundClaimSerializer(read_only=True)
    booking_reference = serializers.CharField(source="booking.reference", read_only=True)
    passenger_ids = serializers.SerializerMethodField()

    class Meta:
        model = CancellationRequest
        fields = [
            "id",
            "booking",
            "booking_reference",
            "requested_by",
            "cancellation_type",
            "status",
            "passenger_ids",
            "cancelled_segment_indexes",
            "reason",
            "rejection_reason",
            "idempotency_key",
            "provider_cancellation_reference",
            "provider_response",
            "refund_claim",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_passenger_ids(self, obj) -> list:
        return [str(p.id) for p in obj.passengers.all()]


class CancellationEstimateSerializer(serializers.Serializer):
    """Read-only response returned from initiate action."""
    cancellation_request = CancellationRequestSerializer(read_only=True)
    eligibility = serializers.DictField(read_only=True)
    estimate = serializers.DictField(read_only=True)


class CancellationAuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationAuditEvent
        fields = "__all__"
