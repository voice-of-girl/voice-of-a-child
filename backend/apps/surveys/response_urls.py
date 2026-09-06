from rest_framework.routers import DefaultRouter

from .views import SurveyResponseViewSet

router = DefaultRouter(trailing_slash=True)
router.register("", SurveyResponseViewSet, basename="survey-response")

urlpatterns = router.urls