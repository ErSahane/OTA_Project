from django.db import models
from django.utils import timezone


class AuditModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


class Country(AuditModelMixin):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = "master_country"

    def __str__(self):
        return self.name


class StateRegion(AuditModelMixin):
    country = models.ForeignKey("master_data.Country", related_name="states", on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "master_state_region"
        unique_together = ("country", "code")

    def __str__(self):
        return f"{self.country.code}-{self.name}"


class City(AuditModelMixin):
    state = models.ForeignKey("master_data.StateRegion", related_name="cities", on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "master_city"
        unique_together = ("state", "code")

    def __str__(self):
        return self.name


class Airport(AuditModelMixin):
    city = models.ForeignKey("master_data.City", related_name="airports", on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "master_airport"

    def __str__(self):
        return self.code


class Airline(AuditModelMixin):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "master_airline"

    def __str__(self):
        return self.code


class Currency(AuditModelMixin):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = "master_currency"

    def __str__(self):
        return self.code


class Language(AuditModelMixin):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "master_language"

    def __str__(self):
        return self.name


class CabinClass(AuditModelMixin):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "master_cabin_class"

    def __str__(self):
        return self.name


class PassengerType(AuditModelMixin):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "master_passenger_type"

    def __str__(self):
        return self.name


class TripType(AuditModelMixin):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "master_trip_type"

    def __str__(self):
        return self.name


class FareType(AuditModelMixin):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "master_fare_type"

    def __str__(self):
        return self.name
