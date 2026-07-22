from rest_framework import serializers

from .models import ProviderConfiguration


class ProviderConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderConfiguration
        fields = [
            "id",
            "provider_name",
            "provider_type",
            "endpoint",
            "api_key",
            "timeout_seconds",
            "retry_count",
            "enabled",
        ]
