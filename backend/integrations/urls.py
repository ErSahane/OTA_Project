from django.urls import path

from .views import ProviderConfigurationListView, ProviderHealthView

app_name = "integrations"

urlpatterns = [
    path("providers/", ProviderConfigurationListView.as_view(), name="provider-list"),
    path("providers/health/", ProviderHealthView.as_view(), name="provider-health"),
]
