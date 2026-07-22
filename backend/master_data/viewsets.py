from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import AuditLog
from accounts.permissions import IsStaffOrAdmin
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
from .serializers import (
    AirlineSerializer,
    AirportSerializer,
    CabinClassSerializer,
    CitySerializer,
    CountrySerializer,
    CurrencySerializer,
    FareTypeSerializer,
    LanguageSerializer,
    PassengerTypeSerializer,
    StateRegionSerializer,
    TripTypeSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class BaseMasterViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrAdmin()]

    def get_queryset(self):
        queryset = self.queryset.filter(is_deleted=False)
        model = self.queryset.model
        filter_params = {}
        for param, value in self.request.query_params.items():
            if param in ["page", "page_size", "search", "ordering"]:
                continue
            try:
                model._meta.get_field(param)
                filter_params[param] = value
            except Exception:
                if param.endswith("_id"):
                    field_name = param[:-3]
                    try:
                        model._meta.get_field(field_name)
                        filter_params[param] = value
                    except Exception:
                        pass
        if filter_params:
            queryset = queryset.filter(**filter_params)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user,
            action=f"{self.queryset.model.__name__.lower()}_create",
            details=f"Created {self.queryset.model.__name__} (ID: {instance.id}, Code: {getattr(instance, 'code', 'N/A')})"
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user,
            action=f"{self.queryset.model.__name__.lower()}_update",
            details=f"Updated {self.queryset.model.__name__} (ID: {instance.id}, Code: {getattr(instance, 'code', 'N/A')})"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        user = request.user if request.user and request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user,
            action=f"{self.queryset.model.__name__.lower()}_delete",
            details=f"Soft deleted {self.queryset.model.__name__} (ID: {instance.id}, Code: {getattr(instance, 'code', 'N/A')})"
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CountryViewSet(BaseMasterViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class StateRegionViewSet(BaseMasterViewSet):
    queryset = StateRegion.objects.all()
    serializer_class = StateRegionSerializer


class CityViewSet(BaseMasterViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class AirportViewSet(BaseMasterViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirlineViewSet(BaseMasterViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer


class CurrencyViewSet(BaseMasterViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class LanguageViewSet(BaseMasterViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class CabinClassViewSet(BaseMasterViewSet):
    queryset = CabinClass.objects.all()
    serializer_class = CabinClassSerializer


class PassengerTypeViewSet(BaseMasterViewSet):
    queryset = PassengerType.objects.all()
    serializer_class = PassengerTypeSerializer


class TripTypeViewSet(BaseMasterViewSet):
    queryset = TripType.objects.all()
    serializer_class = TripTypeSerializer


class FareTypeViewSet(BaseMasterViewSet):
    queryset = FareType.objects.all()
    serializer_class = FareTypeSerializer
