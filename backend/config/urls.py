from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
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
]
