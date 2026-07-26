import secrets
import string
from contextlib import contextmanager
from decimal import Decimal
from datetime import date, datetime, timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.models import AuditLog
from integrations.models import ProviderConfiguration
from integrations.services import ProviderService
from pricing.services import PricingEngine

from .models import Booking, BookingAuditEvent, BookingPassenger, BookingSession


class BookingStateMachine:
    transitions = {
        BookingSession.STATUS_INITIATED: {BookingSession.STATUS_REVALIDATED, BookingSession.STATUS_FAILED, BookingSession.STATUS_EXPIRED},
        BookingSession.STATUS_REVALIDATED: {BookingSession.STATUS_HELD, BookingSession.STATUS_FAILED, BookingSession.STATUS_EXPIRED},
        BookingSession.STATUS_HELD: {BookingSession.STATUS_BOOKED, BookingSession.STATUS_FAILED, BookingSession.STATUS_EXPIRED, BookingSession.STATUS_CANCELLED},
        BookingSession.STATUS_BOOKED: set(),
        BookingSession.STATUS_FAILED: set(),
        BookingSession.STATUS_EXPIRED: set(),
        BookingSession.STATUS_CANCELLED: set(),
    }

    @classmethod
    def transition(cls, session, target):
        if target != session.status and target not in cls.transitions.get(session.status, set()):
            raise ValidationError(f"Invalid booking state transition from {session.status} to {target}.")
        previous = session.status
        session.status = target
        session.save(update_fields=["status", "updated_at"])
        return previous


class ProviderBookingAdapter:
    def __init__(self, provider_name):
        self.configuration = ProviderConfiguration.objects.filter(provider_name=provider_name, enabled=True).first()
        if not self.configuration:
            raise ValidationError(f"Enabled provider configuration not found for {provider_name}.")

    def create_reservation(self, payload):
        return ProviderService(self.configuration).create_booking(payload)


class DistributedLock:
    def __init__(self, name, timeout=30):
        self.name = f"booking-lock:{name}"
        self.timeout = timeout

    @contextmanager
    def acquire(self):
        locked = cache.add(self.name, "1", timeout=self.timeout)
        if not locked:
            raise ValidationError("Booking request is already being processed.")
        try:
            yield
        finally:
            cache.delete(self.name)


class BookingService:
    @staticmethod
    def _token(prefix):
        return f"{prefix}_{secrets.token_urlsafe(18)}"

    @staticmethod
    def _reference():
        alphabet = string.ascii_uppercase + string.digits
        return "BKG" + "".join(secrets.choice(alphabet) for _ in range(9))

    @staticmethod
    def _json_safe(value):
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, list):
            return [BookingService._json_safe(item) for item in value]
        if isinstance(value, dict):
            return {key: BookingService._json_safe(item) for key, item in value.items()}
        return value

    @staticmethod
    def _audit(action, session=None, booking=None, user=None, state_from="", state_to="", details=None):
        details = details or {}
        BookingAuditEvent.objects.create(session=session, booking=booking, user=user, action=action, state_from=state_from, state_to=state_to, details=details)
        AuditLog.objects.create(user=user, action=action, details=str(details))

    @staticmethod
    def _seat_available(selected_offer):
        if selected_offer.get("seat_available", True) is False:
            raise ValidationError("Selected offer no longer has seats available.")

    @staticmethod
    def _revalidate_fare(session):
        quote = PricingEngine.quote(session.pricing_request)
        if Decimal(quote["totals"]["grand_total"]) != session.quoted_total:
            raise ValidationError("Fare revalidation failed because the total price changed.")
        return quote

    @classmethod
    @transaction.atomic
    def create_session(cls, payload, user=None, correlation_id=""):
        idempotency_key = payload.get("idempotency_key") or cls._token("idem")
        existing = BookingSession.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

        cls._seat_available(payload["selected_offer"])
        pricing_request = cls._json_safe(dict(payload["pricing_request"]))
        pricing_request["passengers_detail"] = cls._json_safe(payload["passengers"])
        quote = PricingEngine.quote(pricing_request)
        quoted_total = Decimal(quote["totals"]["grand_total"])
        now = timezone.now()
        session = BookingSession.objects.create(
            user=user,
            session_token=cls._token("bsess"),
            booking_token=cls._token("btoken"),
            idempotency_key=idempotency_key,
            provider_name=payload["provider_name"],
            search_reference=payload.get("search_reference", ""),
            selected_offer=cls._json_safe(payload["selected_offer"]),
            pricing_request=pricing_request,
            quoted_total=quoted_total,
            currency=quote["currency"],
            contact_email=payload["contact"]["email"],
            contact_phone=payload["contact"]["phone"],
            contact_first_name=payload["contact"]["first_name"],
            contact_last_name=payload["contact"]["last_name"],
            correlation_id=correlation_id,
            provider_hold_reference=payload["selected_offer"].get("hold_reference", cls._token("hold")),
            hold_expires_at=now + timedelta(minutes=payload["hold_minutes"]),
            expires_at=now + timedelta(minutes=payload["hold_minutes"]),
        )
        previous = BookingStateMachine.transition(session, BookingSession.STATUS_REVALIDATED)
        cls._audit("booking.session.revalidated", session=session, user=user, state_from=previous, state_to=session.status, details={"quoted_total": str(quoted_total)})
        previous = BookingStateMachine.transition(session, BookingSession.STATUS_HELD)
        cls._audit("booking.session.held", session=session, user=user, state_from=previous, state_to=session.status, details={"hold_expires_at": session.hold_expires_at.isoformat()})
        return session

    @classmethod
    @transaction.atomic
    def confirm_booking(cls, session_token, user=None):
        session = BookingSession.objects.select_for_update().filter(session_token=session_token).first()
        if not session:
            raise NotFound("Booking session not found.")
        if hasattr(session, "booking"):
            return session.booking
        if session.hold_expires_at and session.hold_expires_at < timezone.now():
            previous = BookingStateMachine.transition(session, BookingSession.STATUS_EXPIRED)
            cls._audit("booking.session.expired", session=session, user=user, state_from=previous, state_to=session.status)
            raise ValidationError("Booking hold has expired.")

        with DistributedLock(session.session_token).acquire():
            cls._seat_available(session.selected_offer)
            cls._revalidate_fare(session)
            provider_payload = {
                "booking_token": session.booking_token,
                "search_reference": session.search_reference,
                "selected_offer": session.selected_offer,
                "pricing_request": session.pricing_request,
                "contact": {
                    "email": session.contact_email,
                    "phone": session.contact_phone,
                    "first_name": session.contact_first_name,
                    "last_name": session.contact_last_name,
                },
                "correlation_id": session.correlation_id,
            }
            response = ProviderBookingAdapter(session.provider_name).create_reservation(provider_payload)
            if response.get("status") != "ok":
                previous = BookingStateMachine.transition(session, BookingSession.STATUS_FAILED)
                cls._audit("booking.confirm.failed", session=session, user=user, state_from=previous, state_to=session.status, details=response)
                raise ValidationError(response.get("error", {}).get("message", "Provider booking failed."))

            booking = Booking.objects.create(
                session=session,
                user=user or session.user,
                reference=cls._reference(),
                provider_name=session.provider_name,
                provider_booking_reference=response.get("booking_reference", ""),
                currency=session.currency,
                total_amount=session.quoted_total,
                status=Booking.STATUS_CONFIRMED,
                contact_email=session.contact_email,
                contact_phone=session.contact_phone,
                contact_first_name=session.contact_first_name,
                contact_last_name=session.contact_last_name,
            )
            for passenger in session.pricing_request.get("passengers_detail", []):
                BookingPassenger.objects.create(
                    booking=booking,
                    passenger_type=passenger["passenger_type"],
                    title=passenger.get("title", ""),
                    first_name=passenger["first_name"],
                    last_name=passenger["last_name"],
                    gender=passenger.get("gender", ""),
                    date_of_birth=passenger.get("date_of_birth"),
                    ssr_requests=passenger.get("ssr_codes", []),
                )
            previous = BookingStateMachine.transition(session, BookingSession.STATUS_BOOKED)
            cls._audit("booking.confirmed", session=session, booking=booking, user=user, state_from=previous, state_to=session.status, details={"reference": booking.reference})
            return booking

    @staticmethod
    def serialize_session(session):
        return {
            "session_token": session.session_token,
            "booking_token": session.booking_token,
            "status": session.status,
            "provider_name": session.provider_name,
            "quoted_total": session.quoted_total,
            "currency": session.currency,
            "hold_expires_at": session.hold_expires_at,
        }

    @staticmethod
    def serialize_booking(booking):
        return {
            "reference": booking.reference,
            "provider_name": booking.provider_name,
            "provider_booking_reference": booking.provider_booking_reference,
            "currency": booking.currency,
            "total_amount": booking.total_amount,
            "status": booking.status,
            "contact_email": booking.contact_email,
            "contact_phone": booking.contact_phone,
            "contact_first_name": booking.contact_first_name,
            "contact_last_name": booking.contact_last_name,
            "passengers": [
                {
                    "passenger_type": passenger.passenger_type,
                    "title": passenger.title,
                    "first_name": passenger.first_name,
                    "last_name": passenger.last_name,
                    "gender": passenger.gender,
                    "date_of_birth": passenger.date_of_birth,
                    "ssr_requests": passenger.ssr_requests,
                }
                for passenger in booking.passengers.all()
            ],
        }
