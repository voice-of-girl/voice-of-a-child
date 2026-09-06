"""
Tenant isolation tests, part 2: monitoring, impact and reports.
"""
import pytest

from tests.conftest import make_user

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------
def test_org_a_cannot_access_org_b_monitoring_data(client_a, org_b):
    from apps.monitoring.models import Challenge, Feedback, SupportRequest

    challenge = Challenge.objects.create(organisation=org_b, title="B Challenge")
    feedback = Feedback.objects.create(organisation=org_b, message="B Feedback")
    support = SupportRequest.objects.create(organisation=org_b, description="B Support")

    assert client_a.get(f"/api/monitoring/challenges/{challenge.id}/").status_code == 404
    assert client_a.get(f"/api/monitoring/feedback/{feedback.id}/").status_code == 404
    assert (
        client_a.get(f"/api/monitoring/support-requests/{support.id}/").status_code == 404
    )
    assert client_a.get("/api/monitoring/challenges/").data["count"] == 0
    assert client_a.get("/api/monitoring/feedback/").data["count"] == 0
    assert client_a.get("/api/monitoring/support-requests/").data["count"] == 0


def test_org_a_cannot_update_org_b_challenge(client_a, org_b):
    from apps.monitoring.models import Challenge

    challenge = Challenge.objects.create(organisation=org_b, title="B Challenge")
    res = client_a.patch(
        f"/api/monitoring/challenges/{challenge.id}/",
        {"status": "RESOLVED"},
        format="json",
    )
    assert res.status_code == 404
    challenge.refresh_from_db()
    assert challenge.status == Challenge.Status.OPEN


# ---------------------------------------------------------------------------
# Impact / KPIs / dashboard
# ---------------------------------------------------------------------------
def test_org_a_dashboard_excludes_org_b_data(client_a, org_b):
    from apps.participants.models import Participant

    Participant.objects.create(organisation=org_b, name="B Person")
    res = client_a.get("/api/impact/dashboard/")
    assert res.status_code == 200
    assert res.data["overview"]["enrolment"] == 0
    assert res.data["overview"]["participants_reached"] == 0


def test_org_a_cannot_read_update_or_delete_org_b_kpi(client_a, org_b):
    from apps.impact.models import KPI

    kpi = KPI.objects.create(
        organisation=org_b, name="Secret KPI", current_value=10.0, target=100.0
    )
    base = f"/api/impact/kpis/{kpi.id}/"
    assert client_a.get(base).status_code == 404
    assert client_a.patch(base, {"current_value": 99}, format="json").status_code == 404
    assert client_a.delete(base).status_code == 404
    assert KPI.objects.filter(pk=kpi.pk).exists()


def test_org_a_cannot_see_org_b_impact_project(client_a, org_b):
    from apps.impact.models import ImpactProject

    project = ImpactProject.objects.create(organisation=org_b, name="B Project")
    assert client_a.get(f"/api/impact-projects/{project.id}/").status_code == 404
    assert client_a.get("/api/impact-projects/").data["count"] == 0


def test_org_a_cannot_access_org_b_project_analysis(client_a, org_b):
    from apps.impact.models import ImpactProject

    project = ImpactProject.objects.create(organisation=org_b, name="B Project")
    assert (
        client_a.get(f"/api/impact-projects/{project.id}/analysis/").status_code == 404
    )


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
def test_org_a_cannot_access_org_b_reports(client_a, org_b):
    from apps.reports.models import Report

    report = Report.objects.create(
        organisation=org_b, title="B Report", report_type=Report.ReportType.IMPACT
    )
    assert client_a.get(f"/api/reports/{report.id}/").status_code == 404
    assert client_a.get(f"/api/reports/{report.id}/download/").status_code == 404
    assert client_a.get("/api/reports/").data["count"] == 0


# ---------------------------------------------------------------------------
# Public survey boundary (tenant scoping of anonymous submissions)
# ---------------------------------------------------------------------------
def test_public_submission_scopes_participant_match_to_survey_org(anon, org_a, org_b):
    """An email matching org B's participant must NOT link when answering org A's survey."""
    from apps.participants.models import Participant
    from apps.surveys.models import Survey, SurveyQuestion, SurveyResponse

    Participant.objects.create(
        organisation=org_b, name="B Person", email="shared@x.test"
    )
    survey = Survey.objects.create(
        organisation=org_a, title="A Survey", status=Survey.Status.PUBLISHED
    )
    question = SurveyQuestion.objects.create(
        survey=survey,
        question="Age?",
        question_type=SurveyQuestion.QuestionType.NUMBER,
        order=1,
    )
    res = anon.post(
        f"/api/public/surveys/{survey.public_token}/responses/",
        {
            "respondent_email": "shared@x.test",
            "answers": {str(question.id): 15},
        },
        format="json",
    )
    assert res.status_code == 201
    assert res.data["participant_matched"] is False
    response = SurveyResponse.objects.get(pk=res.data["response_id"])
    assert response.organisation_id == org_a.id
    assert response.participant_id is None


# ---------------------------------------------------------------------------
# Platform admin (explicit permission)
# ---------------------------------------------------------------------------
def test_platform_admin_sees_all_organisations(org_a, org_b):
    from rest_framework.test import APIClient

    platform_admin = make_user(None, "root@platform.test", role="PLATFORM_ADMIN")
    platform_admin.is_staff = True
    platform_admin.is_superuser = True
    platform_admin.save()
    client = APIClient()
    client.force_authenticate(user=platform_admin)
    res = client.get("/api/organisations/")
    assert res.status_code == 200
    names = {o["name"] for o in res.data["results"]}
    assert {"Org A", "Org B"} <= names