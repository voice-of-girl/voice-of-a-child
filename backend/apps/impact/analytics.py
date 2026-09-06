"""Impact analytics endpoints.

All queries are scoped to the caller's organisation at the database level
and use efficient aggregation. Results are shaped for charts.
"""
from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncWeek
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import CanWriteTenantData
from apps.monitoring.models import Challenge
from apps.participants.models import Participant
from apps.programmes.models import Programme
from apps.surveys.models import Survey, SurveyResponse

from .models import KPI
from .serializers import KPISerializer


class KPIViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = KPISerializer

    def get_permissions(self):
        return [CanWriteTenantData()]

    def get_queryset(self):
        qs = KPI.objects.select_related("organisation", "programme", "impact_project")
        programme = self.request.query_params.get("programme")
        if programme:
            qs = qs.filter(programme_id=programme)
        return qs

    def perform_create(self, serializer):
        serializer.save(organisation=self.request.user.organisation)


def _participants(org, params):
    qs = Participant.objects.filter(organisation=org)
    if params.get("programme"):
        qs = qs.filter(programme_id=params["programme"])
    return qs


def _responses(org, params):
    qs = SurveyResponse.objects.filter(organisation=org)
    if params.get("programme"):
        qs = qs.filter(programme_id=params["programme"])
    if params.get("survey"):
        qs = qs.filter(survey_id=params["survey"])
    return qs


def _surveys(org, params):
    qs = Survey.objects.filter(organisation=org)
    if params.get("programme"):
        qs = qs.filter(programme_id=params["programme"])
    return qs


def _programmes(org, params):
    qs = Programme.objects.filter(organisation=org)
    if params.get("programme"):
        qs = qs.filter(id=params["programme"])
    return qs


def _overview(org, params):
    participants = _participants(org, params)
    surveys = _surveys(org, params)
    responses = _responses(org, params)
    programmes = _programmes(org, params)
    enrolment = participants.count()
    reached = participants.exclude(status=Participant.Status.DROPPED_OUT).count()
    completed = participants.filter(status=Participant.Status.COMPLETED).count()
    response_total = responses.filter(status=SurveyResponse.Status.SUBMITTED).count()
    response_rate = round(response_total / enrolment * 100, 1) if enrolment else 0.0
    completion_rate = round(completed / enrolment * 100, 1) if enrolment else 0.0
    return {
        "participants_reached": reached,
        "enrolment": enrolment,
        "survey_responses": response_total,
        "survey_response_rate": min(100.0, response_rate),
        "completion_rate": completion_rate,
        "active_programmes": programmes.filter(status=Programme.Status.ACTIVE).count(),
        "active_surveys": surveys.filter(status=Survey.Status.PUBLISHED).count(),
        "target_participants": programmes.aggregate(total=Sum("target_participants"))["total"] or 0,
    }


def _impact(org, params):
    kpis = _scoped_kpis(org, params)
    return {
        "kpis": [
            {
                "id": str(k.id),
                "kpi": k.name,
                "unit": k.unit,
                "baseline": k.baseline,
                "current": k.current_value,
                "target": k.target,
                "endline": k.endline,
                "progress_percentage": k.progress_percentage,
                "status": k.status,
            }
            for k in kpis
        ],
        "baseline_endline": [
            {
                "kpi": k.name,
                "baseline": k.baseline,
                "endline": k.endline,
                "change": round(k.endline - k.baseline, 2)
                if (k.endline is not None and k.baseline is not None)
                else None,
                "unit": k.unit,
            }
            for k in kpis
            if k.baseline is not None
        ],
    }


def _monitoring(org, params):
    qs = Challenge.objects.filter(organisation=org)
    if params.get("programme"):
        qs = qs.filter(programme_id=params["programme"])
    total = qs.count()
    by_status = dict(qs.values_list("status").annotate(c=Count("id")))
    resolved = by_status.get(Challenge.Status.RESOLVED, 0)
    return {
        "total_challenges": total,
        "open": by_status.get(Challenge.Status.OPEN, 0),
        "in_progress": by_status.get(Challenge.Status.IN_PROGRESS, 0),
        "resolved": resolved,
        "resolution_rate": round(resolved / total * 100, 1) if total else 0.0,
        "challenges_by_category": list(
            qs.values("category").annotate(count=Count("id")).order_by("-count")
        ),
    }


def _survey(org, params):
    surveys = _surveys(org, params)
    responses = _responses(org, params)
    total = responses.count()
    responses_per_survey = list(
        responses.values("survey__title").annotate(count=Count("id")).order_by("-count")
    )
    return {
        "published_surveys": surveys.filter(status=Survey.Status.PUBLISHED).count(),
        "total_responses": total,
        "responses_per_survey": responses_per_survey,
    }


def _scoped_kpis(org, params):
    kpis = KPI.objects.filter(organisation=org)
    if params.get("programme"):
        kpis = kpis.filter(programme_id=params["programme"])
    if params.get("impact_project"):
        kpis = kpis.filter(impact_project_id=params["impact_project"])
    return kpis.select_related("programme", "impact_project").order_by("name")


class DashboardView(APIView):
    """GET /api/impact/dashboard/ — all dashboard sections in one call."""

    permission_classes = [CanWriteTenantData]

    def get(self, request):
        org = request.user.organisation
        params = request.query_params
        return Response(
            {
                "overview": _overview(org, params),
                "impact": _impact(org, params),
                "monitoring": _monitoring(org, params),
                "survey": _survey(org, params),
            }
        )


class StatisticsView(APIView):
    permission_classes = [CanWriteTenantData]

    def get(self, request):
        return Response(_overview(request.user.organisation, request.query_params))


class TrendsView(APIView):
    permission_classes = [CanWriteTenantData]

    def get(self, request):
        org = request.user.organisation
        programme = request.query_params.get("programme")
        since = timezone.now() - timedelta(days=int(request.query_params.get("days", 180)))
        responses_qs = SurveyResponse.objects.filter(organisation=org, submitted_at__gte=since)
        enrolment_qs = Participant.objects.filter(organisation=org, created_at__gte=since)
        if programme:
            responses_qs = responses_qs.filter(programme_id=programme)
            enrolment_qs = enrolment_qs.filter(programme_id=programme)

        responses_per_day = list(
            responses_qs.annotate(day=TruncDate("submitted_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        enrolment_over_time = list(
            enrolment_qs.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return Response(
            {
                "responses_per_day": responses_per_day,
                "enrolment_over_time": enrolment_over_time,
            }
        )


class SurveyResponseRatesView(APIView):
    permission_classes = [CanWriteTenantData]

    def get(self, request):
        org = request.user.organisation
        params = request.query_params
        surveys = _surveys(org, params)
        enrolment = _participants(org, params).count()
        rates = []
        for survey in surveys:
            responses = _responses(org, params).filter(survey=survey).count()
            eligible = _eligible_respondents(org, params, survey)
            rate = round(responses / eligible * 100, 1) if eligible else 0.0
            rates.append(
                {
                    "survey_id": str(survey.id),
                    "survey": survey.title,
                    "responses": responses,
                    "response_rate": min(100.0, rate),
                    "eligible": eligible,
                }
            )
        return Response({"surveys": rates, "enrolment": enrolment})


def _eligible_respondents(org, params, survey):
    """
    Respondents that could have answered this survey.

    Programme surveys use the programme's enrolment as the denominator;
    project surveys use their own responses (no formal enrolment exists).
    """
    if survey.programme_id:
        count = _participants(org, params).filter(programme_id=survey.programme_id).count()
        return count or 1
    if survey.impact_project_id:
        return max(1, survey.responses.count())
    return _participants(org, params).count() or 1


class ChallengeTrendsView(APIView):
    permission_classes = [CanWriteTenantData]

    def get(self, request):
        org = request.user.organisation
        qs = Challenge.objects.filter(organisation=org)
        if request.query_params.get("programme"):
            qs = qs.filter(programme_id=request.query_params["programme"])
        since = timezone.now() - timedelta(days=int(request.query_params.get("days", 90)))
        over_time = list(
            qs.filter(created_at__gte=since)
            .annotate(week=TruncWeek("created_at"))
            .values("week")
            .annotate(count=Count("id"))
            .order_by("week")
        )
        by_category = list(qs.values("category").annotate(count=Count("id")).order_by("-count"))
        return Response({"over_time": over_time, "by_category": by_category})


class BaselineEndlineView(APIView):
    permission_classes = [CanWriteTenantData]

    def get(self, request):
        org = request.user.organisation
        data = _impact(org, request.query_params)
        return Response({"baseline_endline": data["baseline_endline"], "kpis": data["kpis"]})