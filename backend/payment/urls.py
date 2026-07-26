from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PaymentIntentViewSet, PaymentCaptureViewSet, RefundViewSet, webhook_view

router = DefaultRouter()
router.register(r'intent', PaymentIntentViewSet, basename='payment-intent')
router.register(r'capture', PaymentCaptureViewSet, basename='payment-capture')
router.register(r'refund', RefundViewSet, basename='payment-refund')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', webhook_view, name='payment-webhook'),
]
