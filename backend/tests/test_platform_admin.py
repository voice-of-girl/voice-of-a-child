"""
Platform-admin workflow tests: create an organisation, then create an
admin account for it and log in with the returned credentials.
"""
import pytest

from tests.conftest import make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def platform_client():
    from rest_framework.test import APIClient

    admin = make_user(None, "root@platform.test", role="PLATFORM_ADMIN")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


def test_platform_admin_creates_organisation(platform_client):
    res = platform_client.post(
        "/api/admin/organisations/",
        {"name": "New Hope Uganda", "organisation_type": "NGO", "country": "Uganda"},
        format="json",
    )
    assert res.status_code == 201, res.data
    assert res.data["name"] == "New Hope Uganda"
    assert platform_client.get("/api/admin/organisations/").data["count"] >= 1


def test_platform_admin_creates_admin_account_and_can_login(platform_client):
    org_res = platform_client.post(
        "/api/admin/organisations/", {"name": "Rise & Shine"}, format="json"
    )
    org_id = org_res.data["id"]

    res = platform_client.post(
        f"/api/admin/organisations/{org_id}/create-admin/",
        {
            "email": "lead@riseandshine.org",
            "first_name": "Tom",
            "last_name": "Lubega",
        },
        format="json",
    )
    assert res.status_code == 201, res.data
    password = res.data["temporary_password"]
    assert len(password) >= 12  # auto-generated secrets.token_urlsafe

    # The returned credentials must actually work on the login endpoint.
    from rest_framework.test import APIClient

    login = APIClient().post(
        "/api/auth/login/",
        {"email": "lead@riseandshine.org", "password": password},
        format="json",
    )
    assert login.status_code == 200, login.data
    assert "access" in login.data

    # And the new admin sees exactly their own organisation.
    me = APIClient()
    me.force_authenticate(
        __import__("apps.accounts.models", fromlist=["CustomUser"])
        .CustomUser.objects.get(email="lead@riseandshine.org")
    )
    orgs = me.get("/api/organisations/")
    assert orgs.status_code == 200
    assert [o["name"] for o in orgs.data["results"]] == ["Rise & Shine"]


def test_create_admin_rejects_duplicate_email_and_short_password(platform_client):
    org_res = platform_client.post(
        "/api/admin/organisations/", {"name": "Dupe Check"}, format="json"
    )
    org_id = org_res.data["id"]
    assert (
        platform_client.post(
            f"/api/admin/organisations/{org_id}/create-admin/",
            {"email": "a@b.test", "password": "short"},
            format="json",
        ).status_code
        == 400
    )
    platform_client.post(
        f"/api/admin/organisations/{org_id}/create-admin/",
        {"email": "a@b.test"},
        format="json",
    )
    assert (
        platform_client.post(
            f"/api/admin/organisations/{org_id}/create-admin/",
            {"email": "A@b.test"},
            format="json",
        ).status_code
        == 400
    )


def test_org_admin_cannot_create_an_organisation(org_a):
    from rest_framework.test import APIClient

    admin = make_user(org_a, "orgadmin@orga.test", role="ORGANISATION_ADMIN")
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.post("/api/organisations/", {"name": "Sneaky Tenant"}, format="json")
    assert res.status_code == 403


def test_org_admin_cannot_create_users_at_all(org_a):
    """
    Accounts are provisioned exclusively by the platform admin — even for the
    org admin's own organisation.
    """
    from rest_framework.test import APIClient

    admin = make_user(org_a, "orgadmin2@orga.test", role="ORGANISATION_ADMIN")
    client = APIClient()
    client.force_authenticate(user=admin)
    res = client.post(
        "/api/auth/users/",
        {
            "email": "newstaff@orga.test",
            "first_name": "New",
            "last_name": "Staff",
            "role": "STAFF",
            "password": "StrongPass!23",
        },
        format="json",
    )
    assert res.status_code == 403
    from apps.accounts.models import CustomUser

    assert not CustomUser.objects.filter(email="newstaff@orga.test").exists()


def test_platform_admin_creates_user_for_org_with_explicit_password(platform_client, org_a):
    from apps.accounts.models import CustomUser
    from rest_framework.test import APIClient

    res = platform_client.post(
        "/api/admin/users/",
        {
            "email": "officer@orga.test",
            "first_name": "Grace",
            "last_name": "Namulindwa",
            "role": "MONITORING_OFFICER",
            "organisation": str(org_a.id),
            "password": "Measure!t2026",
        },
        format="json",
    )
    assert res.status_code == 201, res.data
    user = CustomUser.objects.get(email="officer@orga.test")
    assert user.organisation_id == org_a.id
    assert user.role == CustomUser.Role.MONITORING_OFFICER
    assert user.check_password("Measure!t2026")

    # The new user can log in immediately.
    login = APIClient().post(
        "/api/auth/login/",
        {"email": "officer@orga.test", "password": "Measure!t2026"},
        format="json",
    )
    assert login.status_code == 200


def test_platform_admin_creates_user_with_generated_password(platform_client, org_a):
    """Omitting the password triggers a secure generated one, returned once."""
    from rest_framework.test import APIClient

    res = platform_client.post(
        "/api/admin/users/",
        {
            "email": "temp@orga.test",
            "first_name": "Temp",
            "last_name": "User",
            "role": "STAFF",
            "organisation": str(org_a.id),
        },
        format="json",
    )
    assert res.status_code == 201, res.data
    password = res.data["temporary_password"]
    assert len(password) >= 12

    login = APIClient().post(
        "/api/auth/login/",
        {"email": "temp@orga.test", "password": password},
        format="json",
    )
    assert login.status_code == 200, login.data


def test_platform_admin_requires_org_for_tenant_roles(platform_client):
    res = platform_client.post(
        "/api/admin/users/",
        {"email": "floating@x.test", "role": "STAFF", "password": "StrongPass!23"},
        format="json",
    )
    assert res.status_code == 400
    assert "organisation" in res.data


def test_platform_admin_lists_users_filtered_by_org(platform_client, org_a, org_b):
    platform_client.post(
        "/api/admin/users/",
        {
            "email": "listed@orga.test",
            "role": "STAFF",
            "organisation": str(org_a.id),
            "password": "StrongPass!23",
        },
        format="json",
    )
    res = platform_client.get(f"/api/admin/users/?organisation={org_a.id}")
    assert res.status_code == 200
    # NOTE: in-process DRF responses keep UUIDs as UUID objects; JSON clients
    # receive strings. Normalise before comparing.
    emails = {u["email"] for u in res.data["results"]}
    assert "listed@orga.test" in emails
    assert all(str(u["organisation"]) == str(org_a.id) for u in res.data["results"])


def test_staff_cannot_create_users(org_a):
    from rest_framework.test import APIClient

    staff = make_user(org_a, "plainstaff@orga.test", role="STAFF")
    client = APIClient()
    client.force_authenticate(user=staff)
    res = client.post(
        "/api/auth/users/",
        {
            "email": "nope@orga.test",
            "first_name": "No",
            "last_name": "Chance",
            "role": "STAFF",
            "password": "StrongPass!23",
        },
        format="json",
    )
    assert res.status_code == 403