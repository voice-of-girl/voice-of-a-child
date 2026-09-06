"""Participant public registration and organisation-scoped access tests."""
import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser
from apps.organisations.models import Organisation
from apps.participants.models import Participant

from apps.accounts.tests import make_org, make_user


class ParticipantRegistrationTests(APITestCase):
    def test_public_registration_creates_participant_without_account(self):
        payload = {
            "full_name": "Sarah Nakato",
            "date_of_birth": "2004-06-15",
            "gender": "FEMALE",
            "phone_number": "+256771234567",
            "district": "Kampala",
            "education_level": "SECONDARY_O_LEVEL",
            "skills": ["Basic computer"],
            "interests": ["Entrepreneurship"],
            "career_goals": "Open a tailoring shop",
            "employment_status": "UNEMPLOYED",
            "registration_source": "Voice of a Girl community form",
        }
        res = self.client.post("/api/participants/register/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        participant = Participant.objects.get(full_name="Sarah Nakato")
        # Registered through a VoA Girl form: org-agnostic and PENDING.
        self.assertIsNone(participant.organisation)
        self.assertEqual(participant.verification_status, Participant.VerificationStatus.PENDING)
        # Participants must NOT receive login credentials.
        self.assertFalse(CustomUser.objects.filter(email__icontains="nakato").exists())

    def test_registration_requires_full_name(self):
        res = self.client.post(
            "/api/participants/register/", {"district": "Kampala"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ParticipantIsolationTests(APITestCase):
    def setUp(self):
        self.org_a = make_org("Org A")
        self.org_b = make_org("Org B")
        self.user_a = make_user("a@test.org", org=self.org_a)
        self.user_b = make_user("b@test.org", org=self.org_b)
        self.admin = make_user("admin@test.org", role=CustomUser.Role.ADMIN)
        self.participant_a = Participant.objects.create(
            organisation=self.org_a, full_name="Girl A", district="Kampala"
        )
        self.participant_b = Participant.objects.create(
            organisation=self.org_b, full_name="Girl B", district="Gulu"
        )

    def auth(self, user):
        refresh = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "Pass@1234"},
            format="json",
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh}")

    def test_org_user_only_sees_own_participants(self):
        self.auth(self.user_a)
        res = self.client.get("/api/participants/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [r["full_name"] for r in res.data["results"]]
        self.assertIn("Girl A", names)
        self.assertNotIn("Girl B", names)

    def test_org_user_cannot_retrieve_other_org_participant(self):
        self.auth(self.user_a)
        res = self.client.get(f"/api/participants/{self.participant_b.id}/")
        self.assertIn(
            res.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_org_user_cannot_delete_other_org_participant(self):
        self.auth(self.user_a)
        res = self.client.delete(f"/api/participants/{self.participant_b.id}/")
        self.assertIn(
            res.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        self.assertTrue(Participant.objects.filter(pk=self.participant_b.id).exists())

    def test_admin_sees_all_participants(self):
        self.auth(self.admin)
        res = self.client.get("/api/participants/")
        names = [r["full_name"] for r in res.data["results"]]
        self.assertIn("Girl A", names)
        self.assertIn("Girl B", names)

    def test_search_and_district_filter(self):
        self.auth(self.user_a)
        res = self.client.get("/api/participants/", {"search": "Girl"})
        self.assertEqual(res.data["count"], 1)
