from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.programmes.views import (
    ProgrammeEnrollmentViewSet,
    ProgrammeKPIViewSet,
    ProgrammeViewSet,
)

router = DefaultRouter()
router.register("kpis", ProgrammeKPIViewSet, basename="programme-kpis")
router.register("enrollments", ProgrammeEnrollmentViewSet, basename="programme-enrollments")
router.register("", ProgrammeViewSet, basename="programmes")

urlpatterns = [
    path("", include(router.urls)),
]