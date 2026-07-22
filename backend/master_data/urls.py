from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ImportExportViewSet
from .viewsets import (
    AirlineViewSet,
    AirportViewSet,
    CabinClassViewSet,
    CityViewSet,
    CountryViewSet,
    CurrencyViewSet,
    FareTypeViewSet,
    LanguageViewSet,
    PassengerTypeViewSet,
    StateRegionViewSet,
    TripTypeViewSet,
)

router = DefaultRouter()
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"states", StateRegionViewSet, basename="state-region")
router.register(r"cities", CityViewSet, basename="city")
router.register(r"airports", AirportViewSet, basename="airport")
router.register(r"airlines", AirlineViewSet, basename="airline")
router.register(r"currencies", CurrencyViewSet, basename="currency")
router.register(r"languages", LanguageViewSet, basename="language")
router.register(r"cabin-classes", CabinClassViewSet, basename="cabin-class")
router.register(r"passenger-types", PassengerTypeViewSet, basename="passenger-type")
router.register(r"trip-types", TripTypeViewSet, basename="trip-type")
router.register(r"fare-types", FareTypeViewSet, basename="fare-type")
router.register(r"import-export", ImportExportViewSet, basename="import-export")

urlpatterns = [path("", include(router.urls))]
