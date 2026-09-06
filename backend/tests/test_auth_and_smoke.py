"""Authentication, permissions and smoke tests."""
import pytest

from tests.conftest import make_user

pytestmark = pytest.mark.django_db


def test_login_returns_jwt(client, org_a):
    user = make_user(org_a, "login@orga.test", password="StrongPass123!")
    res = client.post(
        "/api/auth/login/",
        {"email": "login@orga.test", "password": "StrongPass123!"},
        format="json",
    )
    assert res.status_code == 200
    assert "access" in res.data and "refresh" in res.data


def test_login_rejects_bad_password(client, org_a):
    make_user(org_a, "bad@orga.test", password="StrongPass123!")
    res = client.post(
        "/api/auth/login/",
        {"email": "bad@orga.test", "password": "wrong"},
        format="json",
    )
    assert res.status_code == 401


def test_protected_endpoints_require_authentication(anon):
    for url in [
        "/api/programmes/",
        "/api/participants/",
        "/api/surveys/",
        "/api/monitoring/challenges/",
        "/api/impact/dashboard/",
        "/api/reports/",
        "/api/impact-projects/",
    ]:
        assert anon.get(url).status_code in (401, 403), url


def test_me_endpoint_returns_profile(client, org_a):
    make_user(org_a, "me@orga.test", password="StrongPass123!")
    login = client.post(
        "/api/auth/login/",
        {"email": "me@orga.test", "password": "StrongPass123!"},
        format="json",
    )
    client.headers = {"HTTP_AUTHORIZATION": ""}
    token = login.data["access"]
    res = client.get("/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert res.status_code == 200
    assert res.data["email"] == "me@orga.test"


def test_password_is_hashed(org_a):
    user = make_user(org_a, "hash@orga.test", password="StrongPass123!")
    assert user.password.startswith("pbkdf2_")
    assert "StrongPass123!" not in user.password


def test_programmes_crud_flow(client, org_a):
    make_user(org_a, "crud@orga.test", password="StrongPass123!")
    login = client.post(
        "/api/auth/login/",
        {"email": "crud@orga.test", "password": "StrongPass123!"},
        format="json",
    )
    token = login.data["access"]
    auth = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    created = client.post(
        "/api/programmes/",
        {
            "name": "New Programme",
            "description": "Created by test",
            "start_date": "2026-01-01",
            "status": "ACTIVE",
        },
        format="json",
        **auth,
    )
    assert created.status_code == 201, created.data
    programme_id = created.data["id"]

    listed = client.get("/api/programmes/", **auth)
    assert listed.status_code == 200
    assert listed.data["count"] == 1

    detail = client.get(f"/api/programmes/{programme_id}/", **auth)
    assert detail.status_code == 200
    assert detail.data["name"] == "New Programme"

    updated = client.patch(
        f"/api/programmes/{programme_id}/",
        {"name": "Renamed Programme"},
        format="json",
        **auth,
    )
    assert updated.status_code == 200
    assert updated.data["name"] == "Renamed Programme"

    deleted = client.delete(f"/api/programmes/{programme_id}/", **auth)
    assert deleted.status_code == 204
    assert client.get("/api/programmes/", **auth).data["count"] == 0


def test_pagination_present(client, org_a):
    from apps.participants.models import Participant

    make_user(org_a, "pager@orga.test", password="StrongPass123!")
    login = client.post(
        "/api/auth/login/",
        {"email": "pager@orga.test", "password": "StrongPass123!"},
        format="json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.data['access']}"}
    for i in range(25):
        Participant.objects.create(organisation=org_a, name=f"Person {i:02d}")
    res = client.get("/api/participants/?page_size=10", **auth)
    assert res.status_code == 200
    assert res.data["count"] == 25
    assert len(res.data["results"]) == 10
    assert res.data["next"] is not None


def test_participant_bulk_import(client, org_a):
    make_user(org_a, "import@orga.test", password="StrongPass123!")
    login = client.post(
        "/api/auth/login/",
        {"email": "import@orga.test", "password": "StrongPass123!"},
        format="json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.data['access']}"}
    res = client.post(
        "/api/participants/import/",
        {
            "participants": [
                {"name": "Imported One", "external_reference": "REF-1", "age": 15},
                {"name": "Imported Two", "external_reference": "REF-2", "age": 16},
            ]
        },
        format="json",
        **auth,
    )
    assert res.status_code == 200
    assert res.data["created"] == 2
    # Re-import same references -> updates, not duplicates.
    res2 = client.post(
        "/api/participants/import/",
        {
            "participants": [
                {"name": "Imported One Renamed", "external_reference": "REF-1"}
            ]
        },
        format="json",
        **auth,
    )
    assert res2.data["updated"] == 1
    from apps.participants.models import Participant

    assert Participant.objects.filter(organisation=org_a).count() == 2
