from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .analytics import (
    BaselineEndlineView,
    ChallengeTrendsView,
    DashboardView,
    KPIViewSet,
    StatisticsView,
    SurveyResponseRatesView,
    TrendsView,
)
from .project_views import ImpactProjectViewSet

router = DefaultRouter(trailing_slash=True)
router.register("kpis", KPIViewSet, basename="kpi")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="impact-dashboard"),
    path("statistics/", StatisticsView.as_view(), name="impact-statistics"),
    path("trends/", TrendsView.as_view(), name="impact-trends"),
    path("survey-response-rates/", SurveyResponseRatesView.as_view(), name="impact-response-rates"),
    path("challenge-trends/", ChallengeTrendsView.as_view(), name="impact-challenge-trends"),
    path("baseline-endline/", BaselineEndlineView.as_view(), name="impact-baseline-endline"),
    path("", include(router.urls)),
]