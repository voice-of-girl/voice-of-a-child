"""Authentication, JWT flow and role-permission tests."""
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import CustomUser
from apps.organisations.models import Organisation


def make_org(name="Org A"):
    return Organisation.objects.create(
        name=name, email=f"{name.lower().replace(' ', '')}@test.org", organisation_type="NGO"
    )


def make_user(email, org=None, role=CustomUser.Role.ORGANISATION, password="Pass@1234"):
    return CustomUser.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        role=role,
        organisation=org,
    )


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.org = make_org("Isolation Org A")
        self.org_user = make_user("orga@test.org", org=self.org)
        self.admin = make_user("admin@test.org", role=CustomUser.Role.ADMIN)

    def login(self, email, password="Pass@1234"):
        return self.client.post(
            "/api/auth/login/", {"email": email, "password": password}, format="json"
        )

    def test_login_returns_tokens_user_and_role(self):
        res = self.login("orga@test.org")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], "orga@test.org")
        self.assertEqual(res.data["user"]["role"], "ORGANISATION")
        self.assertEqual(
            res.data["user"]["organisation"]["name"], "Isolation Org A"
        )

    def test_login_with_wrong_password_fails(self):
        res = self.login("orga@test.org", "wrong-password")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_flow(self):
        refresh = self.login("orga@test.org").data["refresh"]
        res = self.client.post(
            "/api/auth/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_me_requires_authentication(self):
        res = self.client.get("/api/auth/me/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        access = self.login("orga@test.org").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = self.client.get("/api/auth/me/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["role"], "ORGANISATION")

    def test_logout_blacklists_refresh_token(self):
        data = self.login("orga@test.org").data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access']}")
        res = self.client.post(
            "/api/auth/logout/", {"refresh": data["refresh"]}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # The blacklisted refresh token must no longer be usable.
        res = self.client.post(
            "/api/auth/refresh/", {"refresh": data["refresh"]}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_users_endpoint_is_admin_only(self):
        access = self.login("orga@test.org").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = self.client.get("/api/auth/users/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        admin_access = self.login("admin@test.org").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access}")
        res = self.client.get("/api/auth/users/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_can_create_organisation_user(self):
        admin_access = self.login("admin@test.org").data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access}")
        res = self.client.post(
            "/api/auth/users/",
            {
                "email": "newuser@test.org",
                "password": "NewPass@123",
                "first_name": "New",
                "last_name": "User",
                "role": "ORGANISATION",
                "organisation_id": self.org.id,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CustomUser.objects.filter(email="newuser@test.org").exists()
        )
