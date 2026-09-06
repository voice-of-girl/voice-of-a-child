from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChallengeViewSet, FeedbackViewSet, SupportRequestViewSet

router = DefaultRouter(trailing_slash=True)
router.register("challenges", ChallengeViewSet, basename="challenge")
router.register("feedback", FeedbackViewSet, basename="feedback")
router.register("support-requests", SupportRequestViewSet, basename="support-request")

urlpatterns = [
    path("", include(router.urls)),
]