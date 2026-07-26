from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking.models import Booking

from .models import CancellationRequest, RefundClaim
from .serializers import (
    CancellationApproveSerializer,
    CancellationEstimateSerializer,
    CancellationInitiateSerializer,
    CancellationRejectSerializer,
    CancellationRequestSerializer,
    RefundClaimSerializer,
)
from .services import CancellationWorkflow


class CancellationRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing cancellation requests.
    Exposes: list, retrieve, initiate, approve, reject.
    """

    serializer_class = CancellationRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CancellationRequest.objects.filter(
            booking__user=self.request.user
        ).select_related("booking", "refund_claim").prefetch_related("passengers", "audit_events")

    @extend_schema(
        request=CancellationInitiateSerializer,
        responses={
            201: CancellationEstimateSerializer,
            400: OpenApiResponse(description="Validation or eligibility error."),
            404: OpenApiResponse(description="Booking not found."),
        },
        description=(
            "Initiate a cancellation request for a booking. "
            "Returns eligibility assessment and refund estimate. "
            "Does NOT execute the GDS cancellation — use /approve for that."
        ),
    )
    @action(detail=False, methods=["post"], url_path="initiate")
    def initiate(self, request):
        serializer = CancellationInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        booking = Booking.objects.filter(
            reference=vd["booking_reference"], user=request.user
        ).first()
        if not booking:
            return Response(
                {"detail": f"Booking '{vd['booking_reference']}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = CancellationWorkflow.initiate_cancellation(
            booking=booking,
            cancellation_type=vd["cancellation_type"],
            idempotency_key=vd["idempotency_key"],
            passenger_ids=[str(pid) for pid in vd.get("passenger_ids", [])],
            segment_indexes=vd.get("segment_indexes", []),
            reason=vd.get("reason", ""),
            user=request.user,
        )

        return Response(
            {
                "cancellation_request": CancellationRequestSerializer(result["cancellation_request"]).data,
                "eligibility": result["eligibility"],
                "estimate": {
                    k: str(v) if hasattr(v, "quantize") else v
                    for k, v in result["estimate"].items()
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        request=CancellationApproveSerializer,
        responses={
            200: RefundClaimSerializer,
            400: OpenApiResponse(description="Cancellation processing error."),
        },
        description=(
            "Approve and execute a pending cancellation request. "
            "Contacts the GDS provider, voids tickets, creates RefundClaim, "
            "and posts ledger entries atomically."
        ),
    )
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        cancellation_request = self.get_object()
        refund_claim = CancellationWorkflow.process_cancellation(
            cancellation_request, user=request.user
        )
        return Response(RefundClaimSerializer(refund_claim).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CancellationRejectSerializer,
        responses={
            200: CancellationRequestSerializer,
            400: OpenApiResponse(description="Cannot reject this request."),
        },
        description="Reject a pending cancellation request with an optional reason.",
    )
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        cancellation_request = self.get_object()
        serializer = CancellationRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated = CancellationWorkflow.reject_cancellation(
            cancellation_request,
            rejection_reason=serializer.validated_data.get("rejection_reason", ""),
            user=request.user,
        )
        return Response(CancellationRequestSerializer(updated).data, status=status.HTTP_200_OK)


class RefundClaimViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset to list and retrieve refund claims for the
    authenticated traveller's bookings.
    """

    serializer_class = RefundClaimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RefundClaim.objects.filter(
            booking__user=self.request.user
        ).select_related("booking", "cancellation_request").prefetch_related("ledger_entries")

    @extend_schema(
        request=None,
        responses={200: RefundClaimSerializer},
        description="Simulate refund settlement (for testing/demo). In production this is triggered by the payment gateway webhook.",
    )
    @action(detail=True, methods=["post"], url_path="settle")
    def settle(self, request, pk=None):
        refund_claim = self.get_object()
        settled = CancellationWorkflow.settle_refund(refund_claim, user=request.user)
        return Response(RefundClaimSerializer(settled).data, status=status.HTTP_200_OK)
