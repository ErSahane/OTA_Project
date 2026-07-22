import uuid
from django.db import models
from django.conf import settings


class FlightSearchQuery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flight_searches"
    )
    trip_type = models.CharField(max_length=20)  # one-way, round-trip, multi-city
    cabin_class = models.CharField(max_length=50)  # code representing cabin class
    passenger_adults = models.PositiveIntegerField(default=1)
    passenger_children = models.PositiveIntegerField(default=0)
    passenger_infants = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "flight_search_query"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Search {self.id} - {self.trip_type}"


class FlightSearchSegment(models.Model):
    query = models.ForeignKey(
        FlightSearchQuery,
        on_delete=models.CASCADE,
        related_name="segments"
    )
    origin = models.CharField(max_length=10)       # Airport/City Code
    destination = models.CharField(max_length=10)  # Airport/City Code
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "flight_search_segment"
        ordering = ["sequence"]

    def __str__(self):
        return f"Segment {self.sequence}: {self.origin} -> {self.destination}"


class FlightSearchLog(models.Model):
    query = models.ForeignKey(
        FlightSearchQuery,
        on_delete=models.CASCADE,
        related_name="provider_logs"
    )
    provider_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)        # success, error
    response_time_ms = models.PositiveIntegerField()
    results_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "flight_search_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log {self.provider_name} - {self.status}"
