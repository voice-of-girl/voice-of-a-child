from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # API Endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/organisations/', include('apps.organisations.urls')),
    path('api/beneficiaries/', include('apps.beneficiaries.urls')),
    path('api/programmes/', include('apps.programmes.urls')),
    path('api/opportunities/', include('apps.opportunities.urls')),
    path('api/applications/', include('apps.applications.urls')),
    path('api/participation/', include('apps.participation.urls')),
    path('api/forms/', include('apps.forms.urls')),
    path('api/monitoring/', include('apps.monitoring.urls')),
    path('api/challenges/', include('apps.challenges.urls')),
    path('api/impact/', include('apps.impact.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/verification/', include('apps.verification.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]
