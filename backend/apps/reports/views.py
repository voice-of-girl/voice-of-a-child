"""Report endpoints: structured JSON reports plus CSV/XLSX exports."""
import csv
import io

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminOrOrganisationUser, user_is_admin
from apps.programmes.models import Programme
from apps.surveys.models import Survey
from apps.organisations.models import Organisation
from apps.analytics.services import (
    baseline_endline_compare,
    challenge_analytics,
    organisation_summary,
    survey_results,
)
from apps.reports.services import (
    build_programme_report,
    programme_participants_csv,
    survey_responses_csv,
)


def _xlsx_response(programme):
    """Two-sheet XLSX workbook: participants and survey responses summary."""
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Participants"
    rows = list(csv.reader(io.StringIO(programme_participants_csv(programme))))
    for row in rows:
        ws.append(row)

    ws2 = wb.create_sheet("Findings")
    ws2.append(["Survey", "Question", "Type", "Response Count", "Metric"])
    for s in programme.surveys.all():
        for r in survey_results(s):
            ws2.append(
                [
                    s.title,
                    r["question_text"],
                    r["question_type"],
                    r["response_count"],
                    str(r["metric"]),
                ]
            )

    buffer = io.BytesIO()
    wb.save(buffer)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="programme-{programme.id}-report.xlsx"'
    )
    return response


def _get_programme(request, pk):
    qs = Programme.objects.select_related("organisation").prefetch_related(
        "objectives", "kpis", "enrollments__participant", "surveys"
    )
    if user_is_admin(request.user):
        return qs.filter(pk=pk).first()
    return qs.filter(pk=pk, organisation_id=request.user.organisation_id).first()


def _get_survey(request, pk):
    qs = Survey.objects.select_related("organisation", "programme")
    if user_is_admin(request.user):
        return qs.filter(pk=pk).first()
    return qs.filter(pk=pk, organisation_id=request.user.organisation_id).first()


class ProgrammeReportView(APIView):
    """Full structured programme report (JSON)."""

    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        programme = _get_programme(request, pk)
        if not programme:
            return Response(
                {"detail": "Programme not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(build_programme_report(programme))


class ProgrammeExportView(APIView):
    """Export programme report data as CSV or XLSX."""

    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        programme = _get_programme(request, pk)
        if not programme:
            return Response(
                {"detail": "Programme not found."}, status=status.HTTP_404_NOT_FOUND
            )
        fmt = request.query_params.get("format", "csv").lower()
        if fmt == "xlsx":
            return _xlsx_response(programme)
        response = HttpResponse(programme_participants_csv(programme), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="programme-{programme.id}-participants.csv"'
        )
        return response


class SurveyResponsesExportView(APIView):
    """Export a survey's submitted responses as flattened CSV."""

    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        survey = _get_survey(request, pk)
        if not survey:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )
        response = HttpResponse(survey_responses_csv(survey), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="survey-{survey.id}-responses.csv"'
        )
        return response


class OrganisationImpactReportView(APIView):
    """Organisation-wide impact report for the requesting organisation."""

    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request):
        if user_is_admin(request.user):
            org_id = request.query_params.get("organisation")
            if not org_id:
                return Response(
                    {"detail": "Admins must pass ?organisation=<id>."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            organisation = Organisation.objects.filter(pk=org_id).first()
        else:
            organisation = Organisation.objects.filter(
                pk=request.user.organisation_id
            ).first()
        if not organisation:
            return Response(
                {"detail": "Organisation not found."}, status=status.HTTP_404_NOT_FOUND
            )

        programme_reports = []
        for p in organisation.programmes.all():
            programme_reports.append(
                {
                    "programme": p.id,
                    "title": p.title,
                    "status": p.status,
                    "baseline_vs_endline": baseline_endline_compare(p),
                    "challenges": challenge_analytics(p),
                }
            )
        return Response(
            {
                "meta": {
                    "report_type": "organisation_impact",
                    "generated_at": timezone.now().isoformat(),
                },
                "organisation": organisation_summary(organisation),
                "programmes": programme_reports,
            }
        )