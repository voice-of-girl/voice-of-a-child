"""Shared fixtures and factories for the platform test suite."""
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.organisations.models import Organisation
from apps.surveys.models import Survey

PASSWORD = "Str0ng!Passw0rd!"


def make_organisation(name="Test Org"):
    return Organisation.objects.create(
        name=name,
        description=f"{name} created for automated tests.",
        email=f"info@{name.lower().replace(' ', '')}.test",
    )


def make_user(org, email, role=CustomUser.Role.ORGANISATION_ADMIN, password=PASSWORD):
    return CustomUser.objects.create_user(
        email=email,
        password=password,
        role=role,
        organisation=org,
        first_name="Test",
        last_name="User",
    )


def make_programme(org, name="Test Programme", **kwargs):
    from datetime import date

    from apps.programmes.models import Programme

    defaults = {
        "description": "A programme created for automated tests.",
        "start_date": date(2026, 1, 1),
    }
    defaults.update(kwargs)
    return Programme.objects.create(organisation=org, name=name, **defaults)


def make_survey(org, programme=None, title="Demo Survey", status=Survey.Status.PUBLISHED,
                start=None, end=None, **kwargs):
    """Survey with one required NUMBER question (order=1) for answer tests."""
    from apps.surveys.models import Survey, SurveyQuestion

    if start is not None:
        kwargs["start_date"] = start
    if end is not None:
        kwargs["end_date"] = end
    survey = Survey.objects.create(
        organisation=org,
        programme=programme,
        title=title,
        status=status,
        **kwargs,
    )
    SurveyQuestion.objects.create(
        survey=survey,
        question="How old are you?",
        question_type=SurveyQuestion.QuestionType.NUMBER,
        required=True,
        order=1,
    )
    return survey


@pytest.fixture
def org_a():
    return make_organisation("Org A")


@pytest.fixture
def org_b():
    return make_organisation("Org B")


@pytest.fixture
def admin_a(org_a):
    return make_user(org_a, "admin@a.test")


@pytest.fixture
def admin_b(org_b):
    return make_user(org_b, "admin@b.test")


@pytest.fixture
def client_a(admin_a):
    client = APIClient()
    client.force_authenticate(user=admin_a)
    return client


@pytest.fixture
def client_b(admin_b):
    client = APIClient()
    client.force_authenticate(user=admin_b)
    return client


@pytest.fixture
def anon():
    return APIClient()


@pytest.fixture
def client():
    """Bare DRF API client for tests that perform their own JWT login."""
    return APIClient()


@pytest.fixture(autouse=True)
def _test_environment(settings, tmp_path_factory):
    """Relax throttles, isolate media uploads and clear the throttle cache."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "login": "1000/min",
            "public_survey": "1000/hour",
            "public_submit": "1000/hour",
            "default": "1000/min",
        },
    }
    settings.MEDIA_ROOT = str(tmp_path_factory.mktemp("media"))
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()
