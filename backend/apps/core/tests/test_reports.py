"""Report generation and organisation-isolation tests."""
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from apps.reports.models import Report
from apps.reports.services import generate_report

from .utils import (
    api_client,
    make_organisation,
    make_participant,
    make_programme,
    make_user,
)


class ReportTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.org = make_organisation("Report Org")
        self.user = make_user("admin@report.org", self.org)
        self.client = api_client(self.user)
        self.programme = make_programme(self.org, name="Report Programme")
        make_participant(self.org, self.programme, "Report Participant")

    def _generate(self, file_format):
        return self.client.post(
            "/api/reports/generate/",
            {
                "report_type": Report.ReportType.IMPACT,
                "title": "Quarterly Impact",
                "file_format": file_format,
                "programme": str(self.programme.id),
            },
            format="json",
        )

    def test_generate_pdf_report(self):
        response = self._generate(Report.FileFormat.PDF)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["status"], Report.Status.READY)
        self.assertTrue(response.data["file"])
        download = self.client.get(response.data["download_url"])
        self.assertEqual(download.status_code, 200)
        self.assertTrue(download.content.startswith(b"%PDF"))

    def test_generate_csv_report(self):
        response = self._generate(Report.FileFormat.CSV)
        self.assertEqual(response.status_code, 201, response.data)
        download = self.client.get(response.data["download_url"])
        self.assertEqual(download.status_code, 200)
        self.assertIn(b",", download.content)

    def test_generate_excel_report(self):
        response = self._generate(Report.FileFormat.EXCEL)
        self.assertEqual(response.status_code, 201, response.data)
        download = self.client.get(response.data["download_url"])
        self.assertEqual(download.status_code, 200)
        # xlsx files are zip archives.
        self.assertTrue(download.content.startswith(b"PK"))

    def test_generate_requires_authentication(self):
        response = APIClient().post(
            "/api/reports/generate/",
            {"report_type": Report.ReportType.IMPACT},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_reports_are_isolated_per_organisation(self):
        other = make_organisation("Other Report Org")
        other_admin = make_user("admin@other.org", other)
        other_programme = make_programme(other, name="Hidden Programme")
        make_participant(other, other_programme, "Hidden Participant")
        report = Report.objects.create(
            organisation=other,
            programme=other_programme,
            report_type=Report.ReportType.PROGRAMME,
            title="Secret Report",
            file_format=Report.FileFormat.PDF,
        )
        generate_report(report)

        self.assertEqual(
            self.client.get(f"/api/reports/{report.id}/").status_code, 404
        )
        self.assertEqual(
            self.client.get(f"/api/reports/{report.id}/download/").status_code, 404
        )
        listed = self.client.get("/api/reports/").data["results"]
        self.assertEqual(listed, [])

    def test_generate_with_foreign_programme_rejected(self):
        foreign = make_organisation("Foreign Org")
        foreign_programme = make_programme(foreign, name="Foreign Programme")
        response = self.client.post(
            "/api/reports/generate/",
            {
                "report_type": Report.ReportType.PROGRAMME,
                "title": "Steal",
                "programme": str(foreign_programme.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)