from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PNRRecordViewSet, TicketViewSet

router = DefaultRouter()
router.register("pnr", PNRRecordViewSet, basename="pnr")
router.register("tickets", TicketViewSet, basename="tickets")

urlpatterns = [
    path("", include(router.urls)),
]
