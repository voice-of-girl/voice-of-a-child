from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.impact_projects.views import ImpactProjectViewSet, ImpactPublicAccessView

router = DefaultRouter()
router.register("", ImpactProjectViewSet, basename="impact-projects")

urlpatterns = [
    path("access/<str:token>/", ImpactPublicAccessView.as_view(), name="impact-public-access"),
    path("", include(router.urls)),
]
