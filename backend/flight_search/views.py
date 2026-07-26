from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import FlightSearchQuery
from .serializers import FlightSearchHistorySerializer, FlightSearchOptionsSerializer, FlightSearchQuerySerializer
from .services import FlightSearchService

SEARCH_PARAMETERS = [
    OpenApiParameter("providers", str, description="Repeatable provider filter."),
    OpenApiParameter("airlines", str, description="Repeatable airline/carrier filter."),
    OpenApiParameter("min_price", float), OpenApiParameter("max_price", float),
    OpenApiParameter("max_stops", int), OpenApiParameter("sort", str, enum=["price", "-price", "duration", "-duration", "stops", "-stops"]),
    OpenApiParameter("page", int), OpenApiParameter("page_size", int),
]


class FlightSearchViewSet(viewsets.ViewSet):
    """Create provider-agnostic one-way, round-trip, and multi-city searches."""

    def get_permissions(self):
        return [IsAuthenticated()] if self.action == "summaries" else [AllowAny()]

    @extend_schema(request=FlightSearchQuerySerializer, parameters=SEARCH_PARAMETERS, responses={200: OpenApiResponse(description="Optimized, paginated aggregated flight-search result."), 400: OpenApiResponse(description="Invalid search or presentation options.")}, description="Search enabled providers; apply optional provider/airline, price, stops, sorting, and pagination options.")
    @action(detail=False, methods=["post"], url_path="search")
    def search(self, request):
        serializer = FlightSearchQuerySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        options = FlightSearchOptionsSerializer(data=request.query_params)
        options.is_valid(raise_exception=True)
        return Response(FlightSearchService.search(serializer.save(), request.headers.get("X-Correlation-ID"), options.validated_data), status=status.HTTP_200_OK)

    @extend_schema(responses=FlightSearchHistorySerializer(many=True), description="Return the authenticated user's search history.")
    @action(detail=False, methods=["get"], url_path="summaries")
    def summaries(self, request):
        searches = FlightSearchQuery.objects.filter(user=request.user).prefetch_related("segments")
        return Response(FlightSearchHistorySerializer(searches, many=True).data)
