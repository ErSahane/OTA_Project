from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CancellationRequestViewSet, RefundClaimViewSet

router = DefaultRouter()
router.register("requests", CancellationRequestViewSet, basename="cancellation-requests")
router.register("refunds", RefundClaimViewSet, basename="refund-claims")

urlpatterns = [
    path("", include(router.urls)),
]
