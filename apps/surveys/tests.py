"""Survey management, secure public link submission and isolation tests."""
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import Programme
from apps.surveys.models import Question, Survey, SurveyResponse

from apps.accounts.tests import make_org, make_user


class SurveyFlowTests(APITestCase):
    def setUp(self):
        self.org_a = make_org("Survey Org A")
        self.org_b = make_org("Survey Org B")
        self.user_a = make_user("sa@test.org", org=self.org_a)
        self.user_b = make_user("sb@test.org", org=self.org_b)
        self.programme = Programme.objects.create(
            organisation=self.org_a, title="P-A", status=Programme.Status.ACTIVE
        )
        self.survey = Survey.objects.create(
            organisation=self.org_a,
            title="Baseline",
            survey_type=Survey.SurveyType.BASELINE,
            programme=self.programme,
            status=Survey.Status.PUBLISHED,
        )
        self.question = Question.objects.create(
            survey=self.survey,
            question_text="Are you employed?",
            question_type=Question.QuestionType.YES_NO,
            order=0,
        )
        self.participant = Participant.objects.create(
            organisation=self.org_a, full_name="Link Girl"
        )
        self.response = SurveyResponse.objects.create(
            survey=self.survey,
            participant=self.participant,
            organisation=self.org_a,
        )

    def auth(self, user):
        access = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "Pass@1234"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_org_user_lists_only_own_surveys(self):
        Survey.objects.create(organisation=self.org_b, title="Other survey")
        self.auth(self.user_a)
        res = self.client.get("/api/surveys/")
        titles = [r["title"] for r in res.data["results"]]
        self.assertIn("Baseline", titles)
        self.assertNotIn("Other survey", titles)

    def test_org_user_cannot_publish_other_org_survey(self):
        other = Survey.objects.create(organisation=self.org_b, title="B survey")
        self.auth(self.user_a)
        res = self.client.post(f"/api/surveys/{other.id}/publish/")
        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_public_link_reveals_survey_without_login(self):
        res = self.client.get(f"/api/surveys/link/{self.response.access_token}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["respondent"]["full_name"], "Link Girl")
        self.assertEqual(res.data["questions"][0]["question_text"], "Are you employed?")

    def test_public_submission_records_answer_and_links_participant(self):
        token = self.response.access_token
        res = self.client.post(
            f"/api/surveys/link/{token}/",
            {"answers": [{"question_id": self.question.id, "value": "Yes"}]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.response.refresh_from_db()
        self.assertTrue(self.response.submitted)
        self.assertEqual(self.response.organisation, self.org_a)
        self.assertEqual(self.response.participant, self.participant)
        answer = self.response.answers.get(question=self.question)
        self.assertEqual(answer.value, "Yes")

    def test_duplicate_public_submission_is_rejected(self):
        token = self.response.access_token
        payload = {"answers": [{"question_id": self.question.id, "value": "No"}]}
        first = self.client.post(f"/api/surveys/link/{token}/", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(f"/api/surveys/link/{token}/", payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_answer_is_rejected(self):
        token = self.response.access_token
        res = self.client.post(f"/api/surveys/link/{token}/", {"answers": []}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token_is_404(self):
        res = self.client.get("/api/surveys/link/not-a-real-token/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_draft_survey_is_not_public(self):
        self.survey.status = Survey.Status.DRAFT
        self.survey.save()
        res = self.client.get(f"/api/surveys/link/{self.response.access_token}/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_completion_rate_endpoint(self):
        self.auth(self.user_a)
        res = self.client.get(f"/api/surveys/{self.survey.id}/completion_rate/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("completion_rate", res.data)
