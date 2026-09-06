from rest_framework.routers import DefaultRouter

from apps.surveys.response_views import SurveyResponseViewSet

router = DefaultRouter()
router.register("", SurveyResponseViewSet, basename="survey-responses")

urlpatterns = router.urls
