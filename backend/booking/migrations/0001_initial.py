import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="BookingSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("session_token", models.CharField(max_length=64, unique=True)),
                ("booking_token", models.CharField(max_length=64, unique=True)),
                ("idempotency_key", models.CharField(max_length=100, unique=True)),
                ("provider_name", models.CharField(max_length=100)),
                ("search_reference", models.CharField(blank=True, max_length=100)),
                ("selected_offer", models.JSONField(blank=True, default=dict)),
                ("pricing_request", models.JSONField(blank=True, default=dict)),
                ("quoted_total", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(max_length=3)),
                ("status", models.CharField(choices=[("initiated", "Initiated"), ("revalidated", "Revalidated"), ("held", "Held"), ("booked", "Booked"), ("failed", "Failed"), ("expired", "Expired"), ("cancelled", "Cancelled")], default="initiated", max_length=20)),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_phone", models.CharField(max_length=30)),
                ("contact_first_name", models.CharField(max_length=150)),
                ("contact_last_name", models.CharField(max_length=150)),
                ("correlation_id", models.CharField(blank=True, max_length=100)),
                ("provider_hold_reference", models.CharField(blank=True, max_length=100)),
                ("hold_expires_at", models.DateTimeField(blank=True, null=True)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="booking_sessions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "booking_session", "ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(max_length=32, unique=True)),
                ("provider_name", models.CharField(max_length=100)),
                ("provider_booking_reference", models.CharField(blank=True, max_length=100)),
                ("currency", models.CharField(max_length=3)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("held", "Held"), ("confirmed", "Confirmed"), ("failed", "Failed"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_phone", models.CharField(max_length=30)),
                ("contact_first_name", models.CharField(max_length=150)),
                ("contact_last_name", models.CharField(max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("session", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="booking", to="booking.bookingsession")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="bookings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "booking", "ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="BookingPassenger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("passenger_type", models.CharField(max_length=10)),
                ("title", models.CharField(blank=True, max_length=20)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("gender", models.CharField(blank=True, max_length=20)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("ssr_requests", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="passengers", to="booking.booking")),
            ],
            options={"db_table": "booking_passenger"},
        ),
        migrations.CreateModel(
            name="BookingAuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=100)),
                ("state_from", models.CharField(blank=True, max_length=20)),
                ("state_to", models.CharField(blank=True, max_length=20)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="audit_events", to="booking.booking")),
                ("session", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="audit_events", to="booking.bookingsession")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "booking_audit_event", "ordering": ("-created_at",)},
        ),
    ]
