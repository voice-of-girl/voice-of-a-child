"""Answer validation and storage helpers shared by all response paths."""
from django.db import transaction

from .models import (
    Survey,
    SurveyAnswer,
    SurveyQuestion,
    SurveyResponse,
)


def validate_answers(survey: Survey, answers: dict):
    """
    Validate a submitted ``answers`` payload against a survey.

    Returns ``(errors, clean_answers)`` where ``errors`` is a dict of
    {question_id: [messages]} and ``clean_answers`` maps question objects to
    their sanitised value. Prevents invalid question ids, wrong value types,
    values outside defined options, and missing required answers.
    """
    questions = {str(q.id): q for q in survey.questions.all()}
    if not isinstance(answers, dict):
        return {"answers": ["Answers must be an object keyed by question id."]}, {}

    errors = {}
    clean = {}

    for qid, raw_value in answers.items():
        if qid not in questions:
            errors.setdefault("answers", []).append(
                f"Question {qid} does not belong to this survey."
            )
            continue
        question = questions[qid]
        value = raw_value
        try:
            value = _normalise_value(question, value)
        except _ValueError as exc:
            errors.setdefault(str(question.id), []).append(str(exc))
            continue
        clean[question] = value

    # Enforce required questions
    for question in questions.values():
        if question.required and question not in clean:
            errors.setdefault(str(question.id), []).append(
                "This question is required."
            )

    return errors, clean


class _ValueError(ValueError):
    """Internal marker for validation failures with a message."""


def _normalise_value(question, value):
    from datetime import date, datetime

    qtype = question.question_type

    if qtype == SurveyQuestion.QuestionType.NUMBER:
        try:
            num = float(value)
            if num != int(num):
                raise _ValueError("Expected a whole number.")
            return int(num)
        except (TypeError, ValueError, OverflowError) as exc:
            if isinstance(exc, _ValueError):
                raise
            raise _ValueError("Expected a whole number.")

    if qtype == SurveyQuestion.QuestionType.DATE:
        try:
            if isinstance(value, str):
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            elif not isinstance(value, (date, datetime)):
                raise _ValueError("Expected a valid ISO date.")
        except (TypeError, ValueError):
            raise _ValueError("Expected a valid ISO date.")
        return value

    if qtype == SurveyQuestion.QuestionType.CHECKBOX:
        if not isinstance(value, list):
            raise _ValueError("Expected a list of selected options.")
        options = set(question.options)
        for item in value:
            if item not in options:
                raise _ValueError(f"'{item}' is not a valid option.")
        return list(value)

    if qtype in {
        SurveyQuestion.QuestionType.MULTIPLE_CHOICE,
        SurveyQuestion.QuestionType.DROPDOWN,
    }:
        if value not in question.options:
            raise _ValueError(f"'{value}' is not a valid option.")
        return value

    if qtype == SurveyQuestion.QuestionType.YES_NO:
        if value is True or value is False:
            return value
        normalized = str(value).strip().lower()
        if normalized in ("yes", "no"):
            return normalized == "yes"
        raise _ValueError("Expected Yes or No.")

    if qtype == SurveyQuestion.QuestionType.RATING_SCALE:
        try:
            num = int(value)
        except (TypeError, ValueError):
            raise _ValueError("Expected a rating between 1 and 5.")
        if not (1 <= num <= 5):
            raise _ValueError("Expected a rating between 1 and 5.")
        return num

    # Text types
    if not isinstance(value, str):
        raise _ValueError("Expected a text answer.")
    return value[:2000]


@transaction.atomic
def store_response(survey, *, organisation, answers, participant=None,
                   impact_project=None, programme=None, respondent_name="",
                   respondent_email="", metadata=None):
    """
    Persist a validated response with its answers.

    ``answers`` must be the ``clean_answers`` mapping produced by
    ``validate_answers`` (question object -> value).
    """
    response = SurveyResponse.objects.create(
        survey=survey,
        organisation=organisation,
        programme=programme or survey.programme,
        participant=participant,
        impact_project=impact_project or survey.impact_project,
        respondent_name=(respondent_name or "").strip(),
        respondent_email=(respondent_email or "").strip().lower(),
        metadata=metadata or {},
    )
    SurveyAnswer.objects.bulk_create(
        [
            SurveyAnswer(response=response, question=question, value=value)
            for question, value in answers.items()
        ]
    )
    return response