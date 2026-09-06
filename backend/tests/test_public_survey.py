"""Public survey system tests (the critical unauthenticated flow)."""
import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.surveys.models import Survey, SurveyQuestion, SurveyResponse
from tests.conftest import make_programme, make_survey

pytestmark = pytest.mark.django_db


def _radio_question(survey, options, order=99):
    return SurveyQuestion.objects.create(
        survey=survey,
        question="Pick one",
        question_type=SurveyQuestion.QuestionType.MULTIPLE_CHOICE,
        options=options,
        order=order,
    )


def _submit(anon, survey, answers, **extra):
    payload = {"answers": answers, **extra}
    return anon.post(
        f"/api/public/surveys/{survey.public_token}/responses/", payload, format="json"
    )


def test_public_token_is_cryptographically_secure(org_a):
    survey = make_survey(org_a)
    token = survey.public_token
    assert len(token) >= 32
    assert token != str(survey.id)
    assert make_survey(org_a).public_token != token


def test_public_survey_get_without_authentication(anon, org_a):
    survey = make_survey(org_a)
    res = anon.get(f"/api/public/surveys/{survey.public_token}/")
    assert res.status_code == 200
    assert res.data["title"] == "Demo Survey"
    assert res.data["accepting_responses"] is True
    assert "public_token" not in res.data
    assert "organisation" not in res.data


def test_public_survey_unknown_token_404(anon):
    assert anon.get(f"/api/public/surveys/{uuid.uuid4().hex}/").status_code == 404


def test_public_submit_valid_response(anon, org_a):
    survey = make_survey(org_a)
    age_q = survey.questions.get(order=1)
    res = _submit(anon, survey, {str(age_q.id): 16}, respondent_name="Walk-in")
    assert res.status_code == 201
    assert res.data["accepted"] is True
    response = SurveyResponse.objects.get(pk=res.data["response_id"])
    assert response.organisation_id == org_a.id
    assert response.submitted_at is not None


def test_public_submit_rejects_invalid_question_id(anon, org_a):
    survey = make_survey(org_a)
    age_q = survey.questions.get(order=1)
    res = _submit(anon, survey, {str(age_q.id): 16, str(uuid.uuid4()): "x"})
    assert res.status_code == 400
    assert not SurveyResponse.objects.filter(survey=survey).exists()


def test_public_submit_rejects_missing_required(anon, org_a):
    survey = make_survey(org_a)
    res = _submit(anon, survey, {})
    assert res.status_code == 400
    assert any("required" in " ".join(m) for m in res.data["errors"].values())


def test_public_submit_rejects_invalid_option(anon, org_a):
    survey = make_survey(org_a)
    mc = _radio_question(survey, ["Red", "Blue"])
    res = _submit(
        anon, survey,
        {str(survey.questions.get(order=1).id): 14, str(mc.id): "Green"},
    )
    assert res.status_code == 400


def test_public_submit_rejects_wrong_type(anon, org_a):
    survey = make_survey(org_a)
    res = _submit(anon, survey, {str(survey.questions.get(order=1).id): "abc"})
    assert res.status_code == 400


def test_closed_survey_rejects_submissions(anon, org_a):
    survey = make_survey(org_a, status=Survey.Status.CLOSED)
    res = _submit(anon, survey, {str(survey.questions.get(order=1).id): 16})
    assert res.status_code == 403
    assert SurveyResponse.objects.filter(survey=survey).count() == 0


def test_draft_survey_rejects_submissions(anon, org_a):
    survey = make_survey(org_a, status=Survey.Status.DRAFT)
    res = _submit(anon, survey, {str(survey.questions.get(order=1).id): 16})
    assert res.status_code == 403


def test_expired_survey_rejects_submissions(anon, org_a):
    survey = make_survey(
        org_a,
        start=timezone.now() - timedelta(days=10),
        end=timezone.now() - timedelta(days=1),
    )
    res = _submit(anon, survey, {str(survey.questions.get(order=1).id): 16})
    assert res.status_code == 403


def test_honeypot_silently_accepts_but_does_not_store(anon, org_a):
    survey = make_survey(org_a)
    res = _submit(
        anon, survey, {str(survey.questions.get(order=1).id): 16},
        website="http://spam.example",
    )
    assert res.status_code == 201
    assert SurveyResponse.objects.filter(survey=survey).count() == 0


def test_malformed_payload_rejected(anon, org_a):
    survey = make_survey(org_a)
    res = anon.post(
        f"/api/public/surveys/{survey.public_token}/responses/",
        {"answers": "not-a-dict"},
        format="json",
    )
    assert res.status_code == 400


def test_duplicate_submission_guard(anon, org_a):
    survey = make_survey(org_a)
    answers = {str(survey.questions.get(order=1).id): 16}
    assert _submit(anon, survey, answers, respondent_email="dupe@x.test").status_code == 201
    assert _submit(anon, survey, answers, respondent_email="dupe@x.test").status_code == 409


def test_email_links_response_to_participant_same_org(anon, org_a):
    from apps.participants.models import Participant

    survey = make_survey(org_a)
    Participant.objects.create(
        organisation=org_a, name="Linked Person", email="link@x.test"
    )
    res = _submit(
        anon, survey, {str(survey.questions.get(order=1).id): 16},
        respondent_email="link@x.test",
    )
    assert res.status_code == 201
    assert res.data["participant_matched"] is True
    response = SurveyResponse.objects.get(pk=res.data["response_id"])
    assert response.participant.email == "link@x.test"


def test_public_response_requires_authentication_to_read(anon):
    assert anon.get("/api/survey-responses/").status_code in (401, 403)


def test_multi_org_public_link_integrity(org_a, org_b, anon):
    """Org B data must never attach to org A's public survey."""
    from apps.participants.models import Participant

    foreign_programme = make_programme(org_b, "B Programme")
    survey = make_survey(org_a)
    res = _submit(anon, survey, {str(survey.questions.get(order=1).id): 15})
    assert res.status_code == 201
    response = SurveyResponse.objects.get(pk=res.data["response_id"])
    assert response.organisation_id == org_a.id
    assert response.programme_id != foreign_programme.id