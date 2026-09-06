"""Root URL configuration for the Voice of a Girl platform."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_v1 = [
    path("auth/", include("apps.accounts.urls")),
    path("organisations/", include("apps.organisations.urls")),
    path("programmes/", include("apps.programmes.urls")),
    path("participants/", include("apps.participants.urls")),
    path("surveys/", include("apps.surveys.urls")),
    path("survey-responses/", include("apps.surveys.response_urls")),
    path("public/surveys/", include("apps.surveys.public_urls")),
    path("monitoring/", include("apps.monitoring.urls")),
    path("impact/", include("apps.impact.urls")),
    path("reports/", include("apps.reports.urls")),
    path("impact-projects/", include("apps.impact.project_urls")),
    path("admin/", include("apps.organisations.platform_admin_urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI / Swagger documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Versioned API routes
    path("api/", include(api_v1)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)