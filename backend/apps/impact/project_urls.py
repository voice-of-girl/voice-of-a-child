from rest_framework.routers import DefaultRouter

from .project_views import ImpactProjectViewSet

router = DefaultRouter(trailing_slash=True)
router.register("", ImpactProjectViewSet, basename="impact-project")

urlpatterns = router.urls