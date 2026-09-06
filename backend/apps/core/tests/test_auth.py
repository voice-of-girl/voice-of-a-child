"""Authentication and access-control tests."""
from django.core.cache import cache
from rest_framework.test import APITestCase

from .utils import PASSWORD, build_two_orgs, jwt_client, make_organisation, make_user


class AuthenticationTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.fx = build_two_orgs()

    def test_login_returns_jwt_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@a.org", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@a.org", "password": "totally-wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoints_require_authentication(self):
        for url in (
            "/api/programmes/",
            "/api/participants/",
            "/api/surveys/",
            "/api/survey-responses/",
            "/api/impact/dashboard/",
            "/api/reports/",
            "/api/auth/users/",
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401, url)

    def test_jwt_grants_access_to_scoped_data(self):
        client = jwt_client(self.fx.admin_a)
        response = client.get("/api/programmes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "A Programme")

    def test_me_endpoint_with_jwt(self):
        client = jwt_client(self.fx.admin_a)
        response = client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data)