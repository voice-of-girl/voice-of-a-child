"""Tenant isolation: Org A must never read, modify or delete Org B data."""
from django.core.cache import cache
from rest_framework.test import APITestCase

from apps.programmes.models import Programme

from .utils import api_client, build_two_orgs


class TenantIsolationTests(APITestCase):
    """Every request below is made by Organisation A's admin."""

    def setUp(self):
        cache.clear()
        self.fx = build_two_orgs()
        self.client = api_client(self.fx.admin_a)

    def test_programme_list_is_scoped(self):
        response = self.client.get("/api/programmes/")
        self.assertEqual(response.status_code, 200)
        names = {row["name"] for row in response.data["results"]}
        self.assertEqual(names, {"A Programme"})

    def test_programme_read_cross_org_returns_404(self):
        response = self.client.get(f"/api/programmes/{self.fx.b_programme.id}/")
        self.assertEqual(response.status_code, 404)

    def test_programme_update_cross_org_returns_404(self):
        response = self.client.patch(
            f"/api/programmes/{self.fx.b_programme.id}/",
            {"name": "Hijacked"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.fx.b_programme.refresh_from_db()
        self.assertEqual(self.fx.b_programme.name, "B Programme")

    def test_programme_delete_cross_org_returns_404(self):
        response = self.client.delete(f"/api/programmes/{self.fx.b_programme.id}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Programme.objects.filter(pk=self.fx.b_programme.pk).exists())

    def test_survey_read_and_responses_cross_org_return_404(self):
        self.assertEqual(
            self.client.get(f"/api/surveys/{self.fx.b_survey.id}/").status_code, 404
        )
        self.assertEqual(
            self.client.get(
                f"/api/surveys/{self.fx.b_survey.id}/responses/"
            ).status_code,
            404,
        )

    def test_survey_response_list_is_scoped(self):
        response = self.client.get("/api/survey-responses/")
        self.assertEqual(response.status_code, 200)
        ids = {row["id"] for row in response.data["results"]}
        self.assertNotIn(str(self.fx.b_response.id), ids)

    def test_participant_list_is_scoped(self):
        response = self.client.get("/api/participants/")
        self.assertEqual(response.status_code, 200)
        names = {row["name"] for row in response.data["results"]}
        self.assertEqual(names, {"A Participant"})

    def test_kpi_list_is_scoped(self):
        response = self.client.get("/api/impact/kpis/")
        self.assertEqual(response.status_code, 200)
        names = {row["name"] for row in response.data["results"]}
        self.assertNotIn("B KPI", names)

    def test_challenge_list_is_scoped(self):
        response = self.client.get("/api/monitoring/challenges/")
        self.assertEqual(response.status_code, 200)
        titles = {row["title"] for row in response.data["results"]}
        self.assertNotIn("B challenge", titles)

    def test_impact_project_list_is_scoped(self):
        response = self.client.get("/api/impact-projects/")
        self.assertEqual(response.status_code, 200)
        names = {row["name"] for row in response.data["results"]}
        self.assertNotIn("B Project", names)

    def test_report_list_is_scoped(self):
        response = self.client.get("/api/reports/")
        self.assertEqual(response.status_code, 200)
        titles = {row["title"] for row in response.data["results"]}
        self.assertNotIn("B Report", titles)

    def test_report_detail_and_download_cross_org_return_404(self):
        report_id = self.fx.b_report.id
        self.assertEqual(
            self.client.get(f"/api/reports/{report_id}/").status_code, 404
        )
        self.assertEqual(
            self.client.get(f"/api/reports/{report_id}/download/").status_code, 404
        )

    def test_dashboard_is_scoped(self):
        response = self.client.get("/api/impact/dashboard/")
        self.assertEqual(response.status_code, 200)
        overview = response.data["overview"]
        self.assertEqual(overview["enrolment"], 1)  # B's participant must not leak