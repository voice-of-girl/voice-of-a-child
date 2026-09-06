from django.urls import path

from apps.reports.views import (
    OrganisationImpactReportView,
    ProgrammeExportView,
    ProgrammeReportView,
    SurveyResponsesExportView,
)

urlpatterns = [
    path(
        "programmes/<int:pk>/",
        ProgrammeReportView.as_view(),
        name="programme-report",
    ),
    path(
        "programmes/<int:pk>/export/",
        ProgrammeExportView.as_view(),
        name="programme-report-export",
    ),
    path(
        "surveys/<int:pk>/responses/export/",
        SurveyResponsesExportView.as_view(),
        name="survey-responses-export",
    ),
    path(
        "organisations/me/",
        OrganisationImpactReportView.as_view(),
        name="organisation-impact-report",
    ),
]