"""Impact analytics calculation tests."""
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from apps.impact.models import KPI
from apps.monitoring.models import Challenge
from apps.participants.models import Participant
from apps.surveys.models import SurveyQuestion
from apps.surveys.services import store_response

from .utils import (
    api_client,
    make_organisation,
    make_participant,
    make_programme,
    make_survey,
    make_user,
)


class AnalyticsTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.org = make_organisation("Analytics Org")
        self.other = make_organisation("Unrelated Org")
        self.user = make_user(
            "mne@analytics.org", self.org, role=CustomUserRole()
        )
        self.client = api_client(self.user)
        self.programme = make_programme(self.org, target_participants=50)
        statuses = (
            [Participant.Status.ACTIVE] * 3
            + [Participant.Status.COMPLETED, Participant.Status.DROPPED_OUT]
        )
        self.participants = [
            make_participant(
                self.org, self.programme, f"Participant {i}", status=status
            )
            for i, status in enumerate(statuses)
        ]
        self.survey = make_survey(
            self.org,
            self.programme,
            questions=[
                {
                    "question": "How are you?",
                    "question_type": SurveyQuestion.QuestionType.SHORT_TEXT,
                }
            ],
        )
        for p in self.participants[:4]:
            store_response(
                self.survey,
                organisation=self.org,
                participant=p,
                answers={self.survey.questions.first(): "ok"},
            )
        # A second organisation whose data must never leak into analytics.
        other_programme = make_programme(self.other, name="Other Programme")
        make_participant(self.other, other_programme, "Other Participant")

    def test_dashboard_overview_calculations(self):
        response = self.client.get("/api/impact/dashboard/")
        self.assertEqual(response.status_code, 200)
        overview = response.data["overview"]
        self.assertEqual(overview["enrolment"], 5)
        self.assertEqual(overview["participants_reached"], 4)
        self.assertEqual(overview["survey_responses"], 4)
        self.assertEqual(overview["survey_response_rate"], 80.0)
        self.assertEqual(overview["completion_rate"], 20.0)
        self.assertEqual(overview["active_programmes"], 1)

    def test_dashboard_excludes_other_organisations(self):
        response = self.client.get("/api/impact/dashboard/")
        self.assertEqual(response.data["overview"]["enrolment"], 5)  # not 6

    def test_kpi_progress_calculation(self):
        KPI.objects.create(
            organisation=self.org,
            programme=self.programme,
            name="Attendance",
            unit="%",
            baseline=50.0,
            current_value=75.0,
            target=100.0,
        )
        response = self.client.get("/api/impact/dashboard/")
        kpis = response.data["impact"]["kpis"]
        self.assertEqual(kpis[0]["kpi"], "Attendance")
        self.assertEqual(kpis[0]["baseline"], 50.0)
        self.assertEqual(kpis[0]["current"], 75.0)
        self.assertEqual(kpis[0]["target"], 100.0)
        self.assertEqual(kpis[0]["progress_percentage"], 50.0)

    def test_baseline_endline_change(self):
        KPI.objects.create(
            organisation=self.org,
            programme=self.programme,
            name="Literacy",
            unit="%",
            baseline=40.0,
            current_value=55.0,
            target=80.0,
            endline=60.0,
        )
        response = self.client.get("/api/impact/baseline-endline/")
        self.assertEqual(response.status_code, 200)
        row = response.data["baseline_endline"][0]
        self.assertEqual(row["kpi"], "Literacy")
        self.assertEqual(row["baseline"], 40.0)
        self.assertEqual(row["endline"], 60.0)
        self.assertEqual(row["change"], 20.0)

    def test_survey_response_rates(self):
        response = self.client.get("/api/impact/survey-response-rates/")
        self.assertEqual(response.status_code, 200)
        entry = response.data["surveys"][0]
        self.assertEqual(entry["survey"], self.survey.title)
        self.assertEqual(entry["responses"], 4)
        self.assertEqual(entry["eligible"], 5)
        self.assertEqual(entry["response_rate"], 80.0)

    def test_challenge_trends_are_scoped(self):
        Challenge.objects.create(
            organisation=self.org, category="TRANSPORT", title="T1", description="d"
        )
        Challenge.objects.create(
            organisation=self.org, category="ATTENDANCE", title="T2", description="d"
        )
        Challenge.objects.create(
            organisation=self.other, category="TRANSPORT", title="T3", description="d"
        )
        response = self.client.get("/api/impact/challenge-trends/")
        total = sum(item["count"] for item in response.data["by_category"])
        self.assertEqual(total, 2)

    def test_programme_statistics(self):
        response = self.client.get(
            f"/api/programmes/{self.programme.id}/statistics/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["enrolment"], 5)
        self.assertEqual(response.data["completed"], 1)
        self.assertEqual(response.data["completion_rate"], 20.0)

    def test_analytics_require_authentication(self):
        response = APIClient().get("/api/impact/dashboard/")
        self.assertEqual(response.status_code, 401)


def CustomUserRole():
    from apps.accounts.models import CustomUser

    return CustomUser.Role.MONITORING_OFFICER