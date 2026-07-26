from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("health/", lambda request: HttpResponse("ok")),
    path("api/", include("core.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/integrations/", include("integrations.urls")),
    path("api/master-data/", include("master_data.urls")),
    path("api/v1/flight-search/", include("flight_search.urls")),
    path("api/v1/pricing/", include("pricing.urls")),
    path("api/v1/bookings/", include("booking.urls")),
    path("api/v1/ticketing/", include("ticketing.urls")),
    path("api/v1/cancellations/", include("cancellation.urls")),
    path('api/v1/payments/', include('payment.urls')),
]
