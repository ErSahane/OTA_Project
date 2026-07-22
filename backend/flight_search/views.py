from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import FlightSearchQuery
from .serializers import FlightSearchQuerySerializer
from .services import FlightSearchService


class FlightSearchViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "summaries":
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=["post"], url_path="search")
    def search(self, request):
        serializer = FlightSearchQuerySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        query = serializer.save()
        results = FlightSearchService.search(query)
        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="summaries")
    def summaries(self, request):
        queryset = FlightSearchQuery.objects.filter(user=request.user).prefetch_related("segments")
        serializer = FlightSearchQuerySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="fare-rules")
    def fare_rules(self, request, pk=None):
        try:
            query = FlightSearchQuery.objects.get(pk=pk)
        except (FlightSearchQuery.DoesNotExist, ValueError):
            return Response({"detail": "Search query not found."}, status=status.HTTP_404_NOT_FOUND)

        rules = [
            {
                "rule_category": "cancellation",
                "rules": "Cancellations made 24 hours prior to departure are subject to a standard provider penalty fee.",
            },
            {
                "rule_category": "baggage",
                "rules": "Standard cabin baggage: 7kg limit. Checked baggage: 20kg limit.",
            },
            {
                "rule_category": "change",
                "rules": "Date change permitted up to 12 hours before departure with a change fee + fare difference.",
            },
        ]
        return Response(
            {"search_id": str(query.id), "cabin_class": query.cabin_class, "fare_rules": rules},
            status=status.HTTP_200_OK,
        )
