"""Authentication and access-control tests."""
import pytest

from tests.conftest import PASSWORD, make_user

pytestmark = pytest.mark.django_db

LOGIN_URL = "/api/auth/login/"
ME_URL = "/api/auth/me/"
PROGRAMMES_URL = "/api/programmes/"


def test_login_returns_tokens(anon, org_a):
    make_user(org_a, "login@a.test")
    res = anon.post(
        LOGIN_URL, {"email": "login@a.test", "password": PASSWORD}, format="json"
    )
    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data


def test_login_rejects_wrong_password(anon, org_a):
    make_user(org_a, "wrongpw@a.test")
    res = anon.post(
        LOGIN_URL, {"email": "wrongpw@a.test", "password": "not-the-password"}, format="json"
    )
    assert res.status_code == 401


def test_login_rejects_unknown_email(anon):
    res = anon.post(
        LOGIN_URL, {"email": "ghost@nowhere.test", "password": PASSWORD}, format="json"
    )
    assert res.status_code == 401


def test_protected_endpoints_require_authentication(anon):
    assert anon.get(PROGRAMMES_URL).status_code == 401
    assert anon.get(ME_URL).status_code == 401
    assert anon.get("/api/impact/dashboard/").status_code == 401


def test_me_returns_current_profile(client_a, admin_a, org_a):
    res = client_a.get(ME_URL)
    assert res.status_code == 200
    assert res.data["email"] == admin_a.email
    assert res.data["role"] == "ORGANISATION_ADMIN"
    assert res.data["organisation"]["id"] == str(org_a.id)


def test_me_cannot_escalate_role_or_org(client_a, admin_a, org_a, org_b):
    res = client_a.patch(
        ME_URL,
        {"role": "PLATFORM_ADMIN", "organisation": str(org_b.id)},
        format="json",
    )
    assert res.status_code == 200
    admin_a.refresh_from_db()
    assert admin_a.role == "ORGANISATION_ADMIN"
    assert admin_a.organisation_id == org_a.id


def test_staff_role_cannot_create_programme(org_a):
    from rest_framework.test import APIClient

    staff = make_user(org_a, "staff@a.test", role="STAFF")
    client = APIClient()
    client.force_authenticate(user=staff)
    res = client.post(PROGRAMMES_URL, {"name": "Nope"}, format="json")
    assert res.status_code == 403


def test_programme_manager_can_write_but_not_delete(org_a):
    from rest_framework.test import APIClient

    manager = make_user(org_a, "manager@a.test", role="PROGRAMME_MANAGER")
    client = APIClient()
    client.force_authenticate(user=manager)
    res = client.post(
        PROGRAMMES_URL,
        {"name": "Manager Programme", "description": "ok", "start_date": "2026-01-01"},
        format="json",
    )
    assert res.status_code == 201
    programme_id = res.data["id"]
    res = client.delete(f"{PROGRAMMES_URL}{programme_id}/")
    assert res.status_code == 403


def test_logout_accepts_refresh_token(anon, org_a):
    from rest_framework.test import APIClient

    make_user(org_a, "logout@a.test")
    tokens = anon.post(
        LOGIN_URL, {"email": "logout@a.test", "password": PASSWORD}, format="json"
    ).data
    client = APIClient()
    client.force_authenticate(user=make_user(org_a, "logout2@a.test"))
    res = client.post("/api/auth/logout/", {"refresh": tokens["refresh"]}, format="json")
    assert res.status_code == 204
