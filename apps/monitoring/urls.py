from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.monitoring.views import ChallengeViewSet

router = DefaultRouter()
router.register("challenges", ChallengeViewSet, basename="challenges")

urlpatterns = [
    path("", include(router.urls)),
]
