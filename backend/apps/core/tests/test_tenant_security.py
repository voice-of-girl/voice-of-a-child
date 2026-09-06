"""Anti-tampering tests: mass assignment, cross-tenant refs, platform admin."""
from django.core.cache import cache
from rest_framework.test import APITestCase

from .utils import api_client, build_two_orgs


class TenantSecurityTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.fx = build_two_orgs()

    def test_participant_mass_assignment_is_ignored(self):
        client = api_client(self.fx.admin_a)
        response = client.post(
            "/api/participants/",
            {"name": "Injected", "organisation": str(self.fx.org_b.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(str(response.data["organisation"]), str(self.fx.org_a.id))

    def test_survey_cannot_reference_foreign_programme(self):
        client = api_client(self.fx.admin_a)
        response = client.post(
            "/api/surveys/",
            {"title": "Bad Survey", "programme": str(self.fx.b_programme.id)},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_report_cannot_be_generated_for_foreign_programme(self):
        client = api_client(self.fx.admin_a)
        response = client.post(
            "/api/reports/generate/",
            {
                "report_type": "PROGRAMME",
                "title": "Steal",
                "programme": str(self.fx.b_programme.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_programme_creation_is_scoped_to_callers_org(self):
        client = api_client(self.fx.admin_a)
        response = client.post(
            "/api/programmes/",
            {"name": "A New Programme", "start_date": "2026-01-15"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(str(response.data["organisation"]), str(self.fx.org_a.id))

    def test_platform_admin_can_access_all_organisations(self):
        client = api_client(self.fx.platform_admin)
        response = client.get("/api/programmes/")
        self.assertEqual(response.status_code, 200)
        names = {row["name"] for row in response.data["results"]}
        self.assertEqual(names, {"A Programme", "B Programme"})