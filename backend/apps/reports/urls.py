from rest_framework.routers import DefaultRouter

from .views import ReportViewSet

router = DefaultRouter(trailing_slash=True)
router.register("", ReportViewSet, basename="report")

urlpatterns = router.urls