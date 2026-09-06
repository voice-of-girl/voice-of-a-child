from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request):
    """Lightweight liveness probe for Render health checks."""
    return JsonResponse({"status": "ok", "service": "voice-of-a-girl-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    # OpenAPI schema & interactive docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Core API routes
    path("api/auth/", include("apps.accounts.urls")),
    path("api/organisations/", include("apps.organisations.urls")),
    path("api/participants/", include("apps.participants.urls")),
    path("api/programmes/", include("apps.programmes.urls")),
    path("api/surveys/", include("apps.surveys.urls")),
    path("api/survey-responses/", include("apps.surveys.response_urls")),
    path("api/monitoring/", include("apps.monitoring.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/impact-projects/", include("apps.impact_projects.urls")),
    # USSD (Africa's Talking)
    path("api/ussd/", include("apps.ussd.urls")),
]
