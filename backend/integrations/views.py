from __future__ import annotations

from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ProviderConfiguration
from .serializers import ProviderConfigurationSerializer
from .services import ProviderService


class ProviderConfigurationListView(ListCreateAPIView):
    queryset = ProviderConfiguration.objects.all()
    serializer_class = ProviderConfigurationSerializer
    permission_classes = [AllowAny]


class ProviderHealthView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        config = ProviderConfiguration.objects.filter(enabled=True).first()
        if not config:
            return Response({"status": "no-provider-configured"}, status=status.HTTP_200_OK)
        service = ProviderService(config)
        result = service.fetch_catalog({"health": True})
        return Response(result, status=status.HTTP_200_OK)
