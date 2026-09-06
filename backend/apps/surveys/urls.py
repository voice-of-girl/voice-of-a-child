from rest_framework.routers import DefaultRouter

from .views import SurveyViewSet

router = DefaultRouter(trailing_slash=True)
router.register("", SurveyViewSet, basename="survey")

urlpatterns = router.urls