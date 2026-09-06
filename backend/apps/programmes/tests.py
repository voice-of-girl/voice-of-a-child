"""Programme CRUD, enrollment and organisation data-isolation tests."""
import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import Programme, ProgrammeEnrollment

from apps.accounts.tests import make_org, make_user


def make_participant(org, name):
    return Participant.objects.create(organisation=org, full_name=name)


class ProgrammeIsolationTests(APITestCase):
    def setUp(self):
        self.org_a = make_org("Prog Org A")
        self.org_b = make_org("Prog Org B")
        self.user_a = make_user("proga@test.org", org=self.org_a)
        self.user_b = make_user("progb@test.org", org=self.org_b)
        self.admin = make_user("admin@test.org", role=CustomUser.Role.ADMIN)
        self.programme_a = Programme.objects.create(
            organisation=self.org_a,
            title="Programme A",
            start_date=datetime.date.today(),
            status=Programme.Status.ACTIVE,
        )
        self.programme_b = Programme.objects.create(
            organisation=self.org_b,
            title="Programme B",
            start_date=datetime.date.today(),
            status=Programme.Status.ACTIVE,
        )

    def auth(self, user):
        access = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "Pass@1234"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_org_user_lists_only_own_programmes(self):
        self.auth(self.user_a)
        res = self.client.get("/api/programmes/")
        titles = [r["title"] for r in res.data["results"]]
        self.assertIn("Programme A", titles)
        self.assertNotIn("Programme B", titles)

    def test_org_user_cannot_read_other_org_programme(self):
        self.auth(self.user_a)
        res = self.client.get(f"/api/programmes/{self.programme_b.id}/")
        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_org_user_cannot_update_other_org_programme(self):
        self.auth(self.user_a)
        res = self.client.patch(
            f"/api/programmes/{self.programme_b.id}/", {"title": "Hacked"}, format="json"
        )
        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.programme_b.refresh_from_db()
        self.assertEqual(self.programme_b.title, "Programme B")

    def test_org_user_cannot_delete_other_org_programme(self):
        self.auth(self.user_a)
        res = self.client.delete(f"/api/programmes/{self.programme_b.id}/")
        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.assertTrue(Programme.objects.filter(pk=self.programme_b.id).exists())

    def test_admin_can_access_all_programmes(self):
        self.auth(self.admin)
        res = self.client.get("/api/programmes/")
        titles = [r["title"] for r in res.data["results"]]
        self.assertIn("Programme A", titles)
        self.assertIn("Programme B", titles)

    def test_programme_crud_by_owner(self):
        self.auth(self.user_a)
        created = self.client.post(
            "/api/programmes/",
            {
                "title": "New Programme",
                "category": "Digital Inclusion",
                "status": "DRAFT",
                "start_date": "2026-01-01",
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Programme.objects.get(pk=created.data["id"]).organisation_id, self.org_a.id
        )

        updated = self.client.patch(
            f"/api/programmes/{created.data['id']}/",
            {"status": "ACTIVE"},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["status"], "ACTIVE")

    def test_assign_participant_to_programme(self):
        participant = make_participant(self.org_a, "Enroll Me")
        self.auth(self.user_a)
        res = self.client.post(
            f"/api/programmes/{self.programme_a.id}/enroll/",
            {"participant_id": participant.id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ProgrammeEnrollment.objects.filter(
                programme=self.programme_a, participant=participant
            ).exists()
        )

    def test_cannot_assign_participant_from_other_organisation(self):
        outsider = make_participant(self.org_b, "Outsider")
        self.auth(self.user_a)
        res = self.client.post(
            f"/api/programmes/{self.programme_a.id}/enroll/",
            {"participant_id": outsider.id},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            ProgrammeEnrollment.objects.filter(participant=outsider).exists()
        )
