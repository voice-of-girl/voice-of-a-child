from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.participants.views import ParticipantRegisterView, ParticipantViewSet

router = DefaultRouter()
router.register("", ParticipantViewSet, basename="participants")

urlpatterns = [
    path("register/", ParticipantRegisterView.as_view(), name="participant-register"),
    path("", include(router.urls)),
]