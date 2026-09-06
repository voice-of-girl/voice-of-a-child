"""Impact-measurement analytics and report isolation tests."""
import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import Programme
from apps.surveys.models import Answer, Question, Survey, SurveyResponse

from apps.accounts.tests import make_org, make_user


class BaselineEndlineTests(APITestCase):
    def setUp(self):
        self.org = make_org("Impact Org")
        self.user = make_user("impact@test.org", org=self.org)
        self.other_org = make_org("Other Impact Org")
        self.other_user = make_user("other@test.org", org=self.other_org)
        self.programme = Programme.objects.create(
            organisation=self.org, title="Impact Programme", status=Programme.Status.ACTIVE
        )
        self.base = Survey.objects.create(
            organisation=self.org,
            title="Baseline",
            survey_type=Survey.SurveyType.BASELINE,
            programme=self.programme,
            status=Survey.Status.PUBLISHED,
        )
        self.end = Survey.objects.create(
            organisation=self.org,
            title="Endline",
            survey_type=Survey.SurveyType.ENDLINE,
            programme=self.programme,
            status=Survey.Status.PUBLISHED,
        )
        self.base_q = Question.objects.create(
            survey=self.base,
            question_text="Employed?",
            question_type=Question.QuestionType.YES_NO,
            order=0,
        )
        self.end_q = Question.objects.create(
            survey=self.end,
            question_text="Employed?",
            question_type=Question.QuestionType.YES_NO,
            order=0,
        )
        # Two respondents per survey: baseline 1/2 = 50%, endline 2/2 = 100%.
        data = [
            (self.base, self.base_q, ["No", "Yes"]),
            (self.end, self.end_q, ["Yes", "Yes"]),
        ]
        for survey, question, values in data:
            for value in values:
                response = SurveyResponse.objects.create(survey=survey, organisation=self.org)
                Answer.objects.create(response=response, question=question, value=value)
                response.submitted = True
                response.submitted_at = datetime.datetime.now(datetime.timezone.utc)
                response.save()

    def auth(self, user):
        access = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "Pass@1234"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_analytics_dashboard_is_scoped_to_organisation(self):
        # Another org's programme must be invisible/unreachable.
        self.auth(self.other_user)
        res = self.client.get(f"/api/analytics/programmes/{self.programme.id}/dashboard/")
        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_baseline_to_endline_comparison(self):
        from apps.analytics.services import baseline_endline_compare

        compare = baseline_endline_compare(self.programme)
        self.assertEqual(len(compare), 1)
        row = compare[0]
        self.assertEqual(row["indicator"], "Employed?")
        # Baseline 1/2 = 50%, endline 2/2 = 100%.
        self.assertEqual(row["percentage"]["baseline"], 50.0)
        self.assertEqual(row["percentage"]["endline"], 100.0)
        self.assertEqual(row["percentage"]["pp_change"], 50.0)

    def test_programme_report_requires_membership(self):
        self.auth(self.other_user)
        res = self.client.get(f"/api/reports/programmes/{self.programme.id}/")
        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_programme_report_returns_full_structure(self):
        self.auth(self.user)
        res = self.client.get(f"/api/reports/programmes/{self.programme.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for section in (
            "meta",
            "overview",
            "objectives",
            "participants",
            "kpi_performance",
            "challenges",
            "outcomes",
            "recommendations",
        ):
            self.assertIn(section, res.data)
        self.assertTrue(res.data["outcomes"]["baseline_vs_endline"])

    def test_csv_export(self):
        self.auth(self.user)
        res = self.client.get(f"/api/reports/programmes/{self.programme.id}/export/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res["Content-Type"], "text/csv")
        self.assertIn("Full Name", res.content.decode())

    def test_survey_responses_export(self):
        self.auth(self.user)
        res = self.client.get(f"/api/reports/surveys/{self.base.id}/responses/export/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("Employed?", res.content.decode())
