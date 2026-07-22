from django.contrib import admin

from .models import (
    Airline,
    Airport,
    CabinClass,
    City,
    Country,
    Currency,
    FareType,
    Language,
    PassengerType,
    StateRegion,
    TripType,
)

admin.site.register(Country)
admin.site.register(StateRegion)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Currency)
admin.site.register(Language)
admin.site.register(CabinClass)
admin.site.register(PassengerType)
admin.site.register(TripType)
admin.site.register(FareType)
