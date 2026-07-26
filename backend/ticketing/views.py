from django.http import HttpResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from booking.models import Booking

from .models import PNRRecord, Ticket
from .serializers import (
    PNRRecordSerializer,
    TicketIssueRequestSerializer,
    TicketReissueRequestSerializer,
    TicketSerializer,
    TicketVoidResponseSerializer,
)
from .services import PNRManager, TicketingService


class PNRRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PNRRecord.objects.all()
    serializer_class = PNRRecordSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "internal_reference"

    @extend_schema(
        request=None,
        responses={200: PNRRecordSerializer, 400: OpenApiResponse(description="PNR sync failed.")},
        description="Sync PNR itinerary data and status from the GDS provider.",
    )
    @action(detail=True, methods=["post"], url_path="sync")
    def sync(self, request, internal_reference=None):
        pnr_record = self.get_object()
        pnr_record = PNRManager.sync_pnr(pnr_record, user=request.user)
        serializer = self.get_serializer(pnr_record)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter tickets by the logged-in traveler
        return Ticket.objects.filter(booking__user=self.request.user)

    @extend_schema(
        request=TicketIssueRequestSerializer,
        responses={201: TicketSerializer(many=True), 400: OpenApiResponse(description="Ticket issuance failed.")},
        description="Idempotently issue electronic tickets for a confirmed booking reference.",
    )
    @action(detail=False, methods=["post"], url_path="issue")
    def issue(self, request):
        serializer = TicketIssueRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_ref = serializer.validated_data["booking_reference"]
        idempotency_key = serializer.validated_data["idempotency_key"]

        booking = Booking.objects.filter(reference=booking_ref, user=request.user).first()
        if not booking:
            return Response({"detail": f"Booking with reference '{booking_ref}' not found."}, status=status.HTTP_404_NOT_FOUND)

        tickets = TicketingService.issue_tickets(booking, idempotency_key, user=request.user)
        response_serializer = TicketSerializer(tickets, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=None,
        responses={200: TicketVoidResponseSerializer, 400: OpenApiResponse(description="Ticket voiding failed.")},
        description="Void an active issued ticket.",
    )
    @action(detail=True, methods=["post"], url_path="void")
    def void(self, request, pk=None):
        ticket = self.get_object()
        voided_ticket = TicketingService.void_ticket(ticket, user=request.user)
        return Response(
            {
                "detail": "Ticket voided successfully.",
                "ticket_number": voided_ticket.ticket_number,
                "status": voided_ticket.status,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=TicketReissueRequestSerializer,
        responses={201: TicketSerializer, 400: OpenApiResponse(description="Ticket reissue failed.")},
        description="Reissue an active issued ticket with new pricing/segments.",
    )
    @action(detail=True, methods=["post"], url_path="reissue")
    def reissue(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketReissueRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_pricing = serializer.validated_data["new_pricing"]
        idempotency_key = serializer.validated_data["idempotency_key"]

        new_ticket = TicketingService.reissue_ticket(ticket, new_pricing, idempotency_key, user=request.user)
        response_serializer = self.get_serializer(new_ticket)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="E-ticket receipt page.")},
        description="Generate and retrieve e-ticket receipt HTML / PDF mockup.",
    )
    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        ticket = self.get_object()
        if not ticket.pdf_content:
            return Response({"detail": "PDF content has not been generated for this ticket."}, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(ticket.pdf_content, content_type="text/html; charset=utf-8")
