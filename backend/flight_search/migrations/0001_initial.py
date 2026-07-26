import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="FlightSearchQuery",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("trip_type", models.CharField(max_length=20)),
                ("cabin_class", models.CharField(max_length=50)),
                ("passenger_adults", models.PositiveIntegerField(default=1)),
                ("passenger_children", models.PositiveIntegerField(default=0)),
                ("passenger_infants", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="flight_searches", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "flight_search_query", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="FlightSearchSegment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("origin", models.CharField(max_length=10)),
                ("destination", models.CharField(max_length=10)),
                ("departure_date", models.DateField()),
                ("return_date", models.DateField(blank=True, null=True)),
                ("sequence", models.PositiveIntegerField(default=0)),
                ("query", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="segments", to="flight_search.flightsearchquery")),
            ],
            options={"db_table": "flight_search_segment", "ordering": ["sequence"]},
        ),
        migrations.CreateModel(
            name="FlightSearchLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider_name", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=50)),
                ("response_time_ms", models.PositiveIntegerField()),
                ("results_count", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("query", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="provider_logs", to="flight_search.flightsearchquery")),
            ],
            options={"db_table": "flight_search_log", "ordering": ["-created_at"]},
        ),
    ]
