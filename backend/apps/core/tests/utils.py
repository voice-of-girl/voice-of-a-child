"""Shared helpers for the automated test suite."""
from datetime import timedelta
from types import SimpleNamespace

from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser
from apps.impact.models import ImpactProject, KPI
from apps.monitoring.models import Challenge
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import Programme
from apps.reports.models import Report
from apps.reports.services import generate_report
from apps.surveys.models import Survey, SurveyQuestion
from apps.surveys.services import store_response

PASSWORD = "Str0ng!Passw0rd!"


def make_organisation(name):
    return Organisation.objects.create(name=name, email=f"info@{name.lower()}.org")


def make_user(email, organisation, role=CustomUser.Role.ORGANISATION_ADMIN):
    return CustomUser.objects.create_user(
        email=email,
        password=PASSWORD,
        first_name="Test",
        last_name="User",
        organisation=organisation,
        role=role,
    )


def make_programme(organisation, name="Girls Education Initiative", **extra):
    params = dict(
        organisation=organisation,
        name=name,
        description="A programme used in tests.",
        start_date=timezone.now().date(),
        status=Programme.Status.ACTIVE,
        target_participants=50,
    )
    params.update(extra)
    return Programme.objects.create(**params)


def make_participant(organisation, programme=None, name="Test Participant", **extra):
    params = dict(
        organisation=organisation,
        programme=programme,
        name=name,
        status=Participant.Status.ACTIVE,
    )
    params.update(extra)
    return Participant.objects.create(**params)


def make_survey(organisation, programme=None, project=None, questions=None, **extra):
    """Create a survey with an ordered list of questions.

    ``questions`` items: {question, question_type, options?, required?}.
    """
    params = dict(
        organisation=organisation,
        programme=programme,
        impact_project=project,
        title=extra.pop("title", "Baseline Survey"),
        stage=extra.pop("stage", Survey.Stage.BASELINE),
        status=extra.pop("status", Survey.Status.PUBLISHED),
        start_date=extra.pop("start_date", timezone.now() - timedelta(days=7)),
        end_date=extra.pop("end_date", timezone.now() + timedelta(days=30)),
    )
    params.update(extra)
    survey = Survey.objects.create(**params)
    for index, q in enumerate(questions or [], start=1):
        SurveyQuestion.objects.create(
            survey=survey,
            order=index,
            question=q["question"],
            question_type=q["question_type"],
            options=q.get("options", []),
            required=q.get("required", True),
        )
    return survey


def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def jwt_client(user):
    """Client authenticated with a real JWT (exercises the auth layer)."""
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


def build_two_orgs():
    """Two organisations with full fixture sets, for isolation tests."""
    fx = SimpleNamespace()
    fx.org_a = make_organisation("Island Org A")
    fx.org_b = make_organisation("Mainland Org B")
    fx.admin_a = make_user("admin@a.org", fx.org_a)
    fx.admin_b = make_user("admin@b.org", fx.org_b)
    fx.platform_admin = make_user(
        "root@platform.org", None, role=CustomUser.Role.PLATFORM_ADMIN
    )
    for tag, org in (("a", fx.org_a), ("b", fx.org_b)):
        programme = make_programme(org, name=f"{tag.upper()} Programme")
        survey = make_survey(
            org,
            programme,
            title=f"{tag.upper()} Survey",
            questions=[
                {
                    "question": "Favourite colour?",
                    "question_type": SurveyQuestion.QuestionType.SHORT_TEXT,
                }
            ],
        )
        response = store_response(
            survey, organisation=org, answers={survey.questions.first(): "blue"}
        )
        make_participant(org, programme, f"{tag.upper()} Participant")
        setattr(fx, f"{tag}_programme", programme)
        setattr(fx, f"{tag}_survey", survey)
        setattr(fx, f"{tag}_response", response)
    fx.b_kpi = KPI.objects.create(
        organisation=fx.org_b,
        programme=fx.b_programme,
        name="B KPI",
        unit="%",
        baseline=10.0,
        current_value=20.0,
        target=50.0,
    )
    fx.b_challenge = Challenge.objects.create(
        organisation=fx.org_b,
        programme=fx.b_programme,
        category="TRANSPORT",
        title="B challenge",
        description="secret",
    )
    fx.b_project = ImpactProject.objects.create(
        organisation=fx.org_b, name="B Project"
    )
    fx.b_report = Report.objects.create(
        organisation=fx.org_b,
        programme=fx.b_programme,
        report_type=Report.ReportType.PROGRAMME,
        title="B Report",
        file_format=Report.FileFormat.CSV,
    )
    generate_report(fx.b_report)
    return fx