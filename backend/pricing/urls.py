from rest_framework.routers import DefaultRouter

from .views import PricingViewSet


router = DefaultRouter()
router.register("", PricingViewSet, basename="pricing")

urlpatterns = router.urls
