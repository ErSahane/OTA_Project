from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingConfirmSerializer, BookingReadSerializer, BookingSessionCreateSerializer, BookingSessionResponseSerializer, BookingStatusSerializer
from .services import BookingService


class BookingViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in {"list", "retrieve", "status"}:
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        request=BookingSessionCreateSerializer,
        responses={200: BookingSessionResponseSerializer, 400: OpenApiResponse(description="Invalid booking session request.")},
        description="Create a held booking session with passenger, contact, SSR, fare revalidation, and seat validation.",
    )
    @action(detail=False, methods=["post"], url_path="sessions")
    def sessions(self, request):
        serializer = BookingSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = BookingService.create_session(serializer.validated_data, user=request.user if request.user.is_authenticated else None, correlation_id=request.headers.get("X-Correlation-ID", ""))
        return Response(BookingService.serialize_session(session), status=status.HTTP_200_OK)

    @extend_schema(
        request=BookingConfirmSerializer,
        responses={200: BookingReadSerializer, 400: OpenApiResponse(description="Booking confirmation failed.")},
        description="Confirm a held booking session into a reservation through the provider abstraction layer.",
    )
    @action(detail=False, methods=["post"], url_path="confirm")
    def confirm(self, request):
        serializer = BookingConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = BookingService.confirm_booking(serializer.validated_data["session_token"], user=request.user if request.user.is_authenticated else None)
        return Response(BookingService.serialize_booking(booking), status=status.HTTP_200_OK)

    @extend_schema(responses=BookingReadSerializer(many=True))
    def list(self, request):
        bookings = Booking.objects.filter(user=request.user).prefetch_related("passengers")
        return Response([BookingService.serialize_booking(booking) for booking in bookings], status=status.HTTP_200_OK)

    @extend_schema(responses=BookingReadSerializer)
    def retrieve(self, request, pk=None):
        booking = Booking.objects.prefetch_related("passengers").filter(reference=pk, user=request.user).first()
        if not booking:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookingService.serialize_booking(booking), status=status.HTTP_200_OK)

    @extend_schema(responses=BookingStatusSerializer)
    @action(detail=True, methods=["get"], url_path="status")
    def status(self, request, pk=None):
        booking = Booking.objects.filter(reference=pk, user=request.user).first()
        if not booking:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"reference": booking.reference, "status": booking.status}, status=status.HTTP_200_OK)
