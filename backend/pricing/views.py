from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import PricingQuoteSerializer
from .services import PricingEngine


class PricingViewSet(viewsets.ViewSet):
    @extend_schema(
        request=PricingQuoteSerializer,
        responses={200: OpenApiResponse(description="Provider-neutral fare rules and pricing quote."), 400: OpenApiResponse(description="Invalid pricing request.")},
        description="Calculate a normalized OTA quote with taxes, markup, service fees, discounts, promo hooks, ancillaries, seats, and fare-rule policies.",
    )
    @action(detail=False, methods=["post"], url_path="quote")
    def quote(self, request):
        serializer = PricingQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(PricingEngine.quote(serializer.validated_data), status=status.HTTP_200_OK)
