from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.surveys.public_views import PublicSurveyLinkView
from apps.surveys.views import SurveyViewSet

router = DefaultRouter()
router.register("", SurveyViewSet, basename="surveys")

urlpatterns = [
    path("link/<str:token>/", PublicSurveyLinkView.as_view(), name="public-survey-link"),
    path("", include(router.urls)),
]
