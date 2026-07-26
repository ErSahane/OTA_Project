from rest_framework.routers import DefaultRouter

from .views import FlightSearchViewSet


router = DefaultRouter()
router.register("", FlightSearchViewSet, basename="flight-search")

urlpatterns = router.urls
