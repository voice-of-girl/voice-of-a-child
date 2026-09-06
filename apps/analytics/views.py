from rest_framework import status, views
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminOrOrganisationUser
from apps.analytics.services import (
    baseline_endline_compare,
    challenge_analytics,
    follow_up_summary,
    kpi_performance,
    organisation_summary,
    programme_dashboard,
    programme_summary,
    survey_results,
)
from apps.organisations.models import Organisation
from apps.programmes.models import Programme
from apps.surveys.models import Survey


def _get_scoped_object(model, obj_id, user, organisation_field="organisation"):
    obj = model.objects.filter(
        id=obj_id,
        **{f"{organisation_field}_id": user.organisation_id}
        if getattr(user, "role", None) == "ORGANISATION"
        else {},
    ).first()
    return obj


class ProgrammeAnalyticsView(views.APIView):
    """Full dashboard analytics for one programme."""

    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        programme = _get_scoped_object(Programme, pk, request.user)
        if not programme:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(programme_dashboard(programme))


class ProgrammeSummaryView(views.APIView):
    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        programme = _get_scoped_object(Programme, pk, request.user)
        if not programme:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(programme_summary(programme))


class ProgrammeKPIReportView(views.APIView):
    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        programme = _get_scoped_object(Programme, pk, request.user)
        if not programme:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"programme": programme.id, "kpis": kpi_performance(programme)})


class ProgrammeOutcomeView(views.APIView):
    """BASELINE -> ENDLINE -> FOLLOW-UP comparison, ready for charts."""

    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        programme = _get_scoped_object(Programme, pk, request.user)
        if not programme:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "baseline_vs_endline": baseline_endline_compare(programme),
                "follow_up": follow_up_summary(programme),
            }
        )


class SurveyAnalyticsView(views.APIView):
    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        survey = _get_scoped_object(Survey, pk, request.user)
        if not survey:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        assigned = survey.assignments.exclude(participant__isnull=True).count()
        submitted = survey.responses.filter(submitted=True).count()
        data = survey_results(survey)
        data["assigned"] = assigned
        data["submitted"] = submitted
        data["completion_rate"] = round((submitted / assigned) * 100, 1) if assigned else 0.0
        return Response(data)


class ChallengeAnalyticsView(views.APIView):
    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request):
        user = request.user
        if getattr(user, "role", None) == "ORGANISATION":
            from apps.monitoring.models import Challenge

            challenges = Challenge.objects.filter(organisation_id=user.organisation_id)
            return Response(challenge_analytics_for_qs(challenges))
        return Response(challenge_analytics())

    def get_object(self):
        return None


def challenge_analytics_for_qs(challenges):
    from django.db.models import Count

    total = challenges.count()
    open_count = challenges.filter(
        status__in=["OPEN", "IN_PROGRESS"]
    ).count()
    resolved = challenges.filter(status="RESOLVED").count()
    return {
        "total": total,
        "open": open_count,
        "resolved": resolved,
        "resolution_rate": round((resolved / total) * 100, 1) if total else 0.0,
        "by_category": list(challenges.values("category").annotate(count=Count("id")).order_by("-count")),
        "by_status": list(challenges.values("status").annotate(count=Count("id")).order_by()),
    }


class OrganisationAnalyticsView(views.APIView):
    permission_classes = [IsAdminOrOrganisationUser]

    def get(self, request, pk):
        if (
            getattr(request.user, "role", None) == "ORGANISATION"
            and request.user.organisation_id != pk
        ):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        organisation = Organisation.objects.filter(id=pk).first()
        if not organisation:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(organisation_summary(organisation))