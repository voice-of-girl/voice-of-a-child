"""
Organisation (tenant) isolation tests.

These prove that Organisation A can never read, modify or delete
Organisation B's data through any API surface.
"""
import pytest

from tests.conftest import make_programme

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Programmes
# ---------------------------------------------------------------------------
def test_org_a_cannot_list_org_b_programmes(client_a, org_b):
    make_programme(org_b, "Secret B Programme")
    res = client_a.get("/api/programmes/")
    assert res.status_code == 200
    names = [p["name"] for p in res.data["results"]]
    assert "Secret B Programme" not in names


def test_org_a_cannot_read_org_b_programme(client_a, org_b):
    programme = make_programme(org_b, "Secret B Programme")
    assert client_a.get(f"/api/programmes/{programme.id}/").status_code == 404


def test_org_a_cannot_update_org_b_programme(client_a, org_b):
    from apps.programmes.models import Programme

    programme = make_programme(org_b, "Secret B Programme")
    res = client_a.patch(
        f"/api/programmes/{programme.id}/", {"name": "Hacked"}, format="json"
    )
    assert res.status_code == 404
    programme.refresh_from_db()
    assert programme.name == "Secret B Programme"


def test_org_a_cannot_delete_org_b_programme(client_a, org_b):
    from apps.programmes.models import Programme

    programme = make_programme(org_b, "Secret B Programme")
    assert client_a.delete(f"/api/programmes/{programme.id}/").status_code == 404
    assert Programme.objects.filter(pk=programme.pk).exists()


# ---------------------------------------------------------------------------
# Participants
# ---------------------------------------------------------------------------
def test_org_a_cannot_list_org_b_participants(client_a, org_b):
    from apps.participants.models import Participant

    Participant.objects.create(organisation=org_b, name="Hidden Person")
    res = client_a.get("/api/participants/")
    names = [p["name"] for p in res.data["results"]]
    assert "Hidden Person" not in names


def test_org_a_cannot_read_update_or_delete_org_b_participant(client_a, org_b):
    from apps.participants.models import Participant

    participant = Participant.objects.create(organisation=org_b, name="Hidden Person")
    base = f"/api/participants/{participant.id}/"
    assert client_a.get(base).status_code == 404
    assert client_a.patch(base, {"name": "Changed"}, format="json").status_code == 404
    assert client_a.delete(base).status_code == 404
    assert Participant.objects.filter(pk=participant.pk).exists()


def test_participant_cannot_reference_foreign_programme(client_a, org_b):
    foreign = make_programme(org_b, "Foreign Programme")
    res = client_a.post(
        "/api/participants/",
        {"name": "Sneaky", "programme": str(foreign.id)},
        format="json",
    )
    assert res.status_code == 400


def test_participant_create_ignores_client_organisation(client_a, org_a, org_b):
    """Mass-assignment defence: organisation comes from the token, not the body."""
    res = client_a.post(
        "/api/participants/",
        {"name": "Honest", "organisation": str(org_b.id)},
        format="json",
    )
    assert res.status_code == 201
    from apps.participants.models import Participant

    participant = Participant.objects.get(pk=res.data["id"])
    assert participant.organisation_id == org_a.id


# ---------------------------------------------------------------------------
# Surveys and responses
# ---------------------------------------------------------------------------
def _make_survey(org, programme=None, status="PUBLISHED"):
    from apps.surveys.models import Survey, SurveyQuestion

    survey = Survey.objects.create(
        organisation=org,
        programme=programme,
        title="B Survey",
        status=status,
    )
    SurveyQuestion.objects.create(
        survey=survey,
        question="Age?",
        question_type=SurveyQuestion.QuestionType.NUMBER,
        order=1,
    )
    return survey


def test_org_a_cannot_access_org_b_survey_or_responses(client_a, org_b):
    from apps.surveys.models import SurveyResponse

    survey = _make_survey(org_b)
    SurveyResponse.objects.create(survey=survey, organisation=org_b)

    assert client_a.get(f"/api/surveys/{survey.id}/").status_code == 404
    assert client_a.get(f"/api/surveys/{survey.id}/responses/").status_code == 404
    assert client_a.get("/api/survey-responses/").data["count"] == 0
    response_id = SurveyResponse.objects.first().id
    assert client_a.get(f"/api/survey-responses/{response_id}/").status_code == 404


def test_org_a_cannot_update_or_delete_org_b_survey(client_a, org_b):
    from apps.surveys.models import Survey

    survey = _make_survey(org_b)
    assert (
        client_a.patch(
            f"/api/surveys/{survey.id}/", {"title": "Hacked"}, format="json"
        ).status_code
        == 404
    )
    assert client_a.delete(f"/api/surveys/{survey.id}/").status_code == 404
    assert Survey.objects.filter(pk=survey.pk).exists()


def test_survey_cannot_reference_foreign_programme(client_a, org_b):
    foreign = make_programme(org_b, "Foreign Programme")
    res = client_a.post(
        "/api/surveys/",
        {"title": "Cross Tenant", "programme": str(foreign.id)},
        format="json",
    )
    assert res.status_code == 400


def test_org_a_cannot_publish_or_close_org_b_survey(client_a, org_b):
    survey = _make_survey(org_b, status="DRAFT")
    assert client_a.post(f"/api/surveys/{survey.id}/publish/").status_code == 404
    assert client_a.post(f"/api/surveys/{survey.id}/close/").status_code == 404
