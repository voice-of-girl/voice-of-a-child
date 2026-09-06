from django.urls import path

from apps.analytics.views import (
    ChallengeAnalyticsView,
    OrganisationAnalyticsView,
    ProgrammeAnalyticsView,
    ProgrammeKPIReportView,
    ProgrammeOutcomeView,
    ProgrammeSummaryView,
    SurveyAnalyticsView,
)

urlpatterns = [
    path("programmes/<int:pk>/", ProgrammeAnalyticsView.as_view(), name="programme-analytics"),
    path("programmes/<int:pk>/summary/", ProgrammeSummaryView.as_view(), name="programme-summary"),
    path("programmes/<int:pk>/kpis/", ProgrammeKPIReportView.as_view(), name="programme-kpi-report"),
    path("programmes/<int:pk>/outcomes/", ProgrammeOutcomeView.as_view(), name="programme-outcomes"),
    path("surveys/<int:pk>/", SurveyAnalyticsView.as_view(), name="survey-analytics"),
    path("challenges/", ChallengeAnalyticsView.as_view(), name="challenge-analytics"),
    path("organisations/<int:pk>/", OrganisationAnalyticsView.as_view(), name="organisation-analytics"),
]
