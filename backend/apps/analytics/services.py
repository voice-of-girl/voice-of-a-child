"""Aggregation and impact-measurement logic for the analytics APIs.

All metrics are computed on demand — nothing is hardcoded — so KPIs and
measurements stay flexible across different programmes.
"""
from collections import Counter

from django.db.models import Count

from apps.monitoring.models import Challenge
from apps.programmes.models import ProgrammeEnrollment
from apps.surveys.models import Answer, Question, Survey

RATING_MAX = 5


def programme_summary(programme):
    """Core participant counts and rates for a programme."""
    enrollments = programme.enrollments.all()
    total = enrollments.count()
    by_status = {
        row["status"]: row["count"]
        for row in enrollments.values("status").annotate(count=Count("id")).order_by()
    }

    active = by_status.get(ProgrammeEnrollment.Status.ACTIVE, 0)
    completed = by_status.get(ProgrammeEnrollment.Status.COMPLETED, 0)
    dropped = by_status.get(ProgrammeEnrollment.Status.DROPPED_OUT, 0)

    active_or_completed = active + completed
    completion_rate = round((active_or_completed / total) * 100, 1) if total else 0.0
    formal_completion_rate = round((completed / total) * 100, 1) if total else 0.0
    dropout_rate = round((dropped / total) * 100, 1) if total else 0.0
    avg_progress = (
        round(sum(e.progress for e in enrollments) / total, 1) if total else 0.0
    )

    return {
        "programme": programme.id,
        "title": programme.title,
        "target_participants": programme.target_participants,
        "participants_reached": total,
        "enrolled": by_status.get(ProgrammeEnrollment.Status.ENROLLED, 0),
        "active": active,
        "completed": completed,
        "dropped_out": dropped,
        "completion_rate": completion_rate,
        "formal_completion_rate": formal_completion_rate,
        "dropout_rate": dropout_rate,
        "average_progress": avg_progress,
    }


def kpi_performance(programme):
    kpis = programme.kpis.all()
    return [
        {
            "id": kpi.id,
            "name": kpi.name,
            "category": kpi.category,
            "unit": kpi.unit,
            "target_value": kpi.target_value,
            "current_value": kpi.current_value,
            "baseline_value": kpi.baseline_value,
            "progress_percentage": kpi.progress_percentage,
            "percentage_change": kpi.percentage_change,
            "percentage_point_change": kpi.percentage_point_change,
        }
        for kpi in kpis
    ]


def _value_to_number(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _question_answers(survey):
    """Return {question_id: {question, values}} for submitted responses only."""
    submitted_ids = survey.responses.filter(submitted=True).values_list("id", flat=True)
    answers = (
        Answer.objects.filter(response_id__in=submitted_ids)
        .select_related("question")
        .order_by("question__order")
    )
    grouped = {}
    for a in answers:
        entry = grouped.setdefault(a.question_id, {"question": a.question, "values": []})
        entry["values"].append(a.value)
    return grouped


def survey_results(survey):
    """Answer distributions for a single survey (submitted responses only)."""
    grouped = _question_answers(survey)
    results = []
    for question_id, entry in grouped.items():
        question = entry["question"]
        values = entry["values"]
        item = {
            "question_id": question_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "response_count": len(values),
            "metric": _metric_for_question(question, values),
        }
        if question.question_type in (
            Question.QuestionType.MULTIPLE_CHOICE,
            Question.QuestionType.DROPDOWN,
        ):
            item["distribution"] = dict(Counter(str(v) for v in values))
        elif question.question_type == Question.QuestionType.CHECKBOX:
            counter = Counter()
            for v in values:
                if isinstance(v, list):
                    counter.update(str(x) for x in v)
                else:
                    counter[str(v)] += 1
            item["distribution"] = dict(counter)
        results.append(item)
    return results


def _metric_for_question(question, values):
    """Return a comparable metric for the baseline-to-endline comparison."""
    if question.question_type == Question.QuestionType.NUMBER:
        numbers = [_value_to_number(v) for v in values]
        numbers = [n for n in numbers if n is not None]
        return {
            "type": "average",
            "average": round(sum(numbers) / len(numbers), 2) if numbers else None,
            "percentage": None,
        }
    if question.question_type == Question.QuestionType.RATING:
        numbers = [_value_to_number(v) for v in values]
        numbers = [n for n in numbers if n is not None]
        avg = round(sum(numbers) / len(numbers), 2) if numbers else None
        max_val = float(max(question.options)) if question.options else RATING_MAX
        return {
            "type": "rating",
            "average": avg,
            "percentage": round((avg / max_val) * 100, 1) if avg is not None else None,
        }
    if question.question_type == Question.QuestionType.YES_NO:
        yes = sum(1 for v in values if str(v).lower() in ("yes", "true", "1"))
        return {
            "type": "yes_no",
            "percentage": round((yes / len(values)) * 100, 1) if values else 0.0,
        }
    return {"type": "unsupported", "percentage": None, "average": None}


def baseline_endline_compare(programme):
    """Compare matched questions across BASELINE and ENDLINE surveys.

    Questions are matched by question_text so the same indicators are
    compared before and after the programme.
    """
    surveys = programme.surveys.all()

    base_surveys = list(surveys.filter(survey_type=Survey.SurveyType.BASELINE))
    end_surveys = list(surveys.filter(survey_type=Survey.SurveyType.ENDLINE))
    if not base_surveys or not end_surveys:
        return []

    # Collect submissions grouped by question_text for each stage.
    def stage_entries(survey_list):
        entries = {}
        for s in survey_list:
            for qid, entry in _question_answers(s).items():
                if entry["values"]:
                    key = entry["question"].question_text
                    existing = entries.setdefault(
                        key, {"question": entry["question"], "values": []}
                    )
                    existing["values"].extend(entry["values"])
        return entries

    base_entries = stage_entries(base_surveys)
    end_entries = stage_entries(end_surveys)

    compare = []
    for indicator, base_entry in base_entries.items():
        end_entry = end_entries.get(indicator)
        if not end_entry:
            continue
        question = base_entry["question"]
        base_metric = _metric_for_question(question, base_entry["values"])
        end_metric = _metric_for_question(question, end_entry["values"])
        if base_metric["type"] == "unsupported":
            continue

        percentage = None
        if base_metric["percentage"] is not None and end_metric["percentage"] is not None:
            pct_change = (
                round(
                    ((end_metric["percentage"] - base_metric["percentage"])
                     / base_metric["percentage"]) * 100,
                    1,
                )
                if base_metric["percentage"] != 0
                else (100.0 if end_metric["percentage"] != 0 else 0.0)
            )
            percentage = {
                "baseline": base_metric["percentage"],
                "endline": end_metric["percentage"],
                "pct_change": pct_change,
                "pp_change": round(end_metric["percentage"] - base_metric["percentage"], 1),
            }

        average = None
        base_avg = base_metric.get("average")
        end_avg = end_metric.get("average")
        if base_avg is not None and end_avg is not None:
            average = {
                "baseline": base_avg,
                "endline": end_avg,
                "pct_change": (
                    round(
                        ((end_avg - base_avg) / base_avg) * 100,
                        1,
                    )
                    if base_avg != 0
                    else (100.0 if end_avg != 0 else 0.0)
                ),
            }

        compare.append(
            {
                "indicator": indicator,
                "question_type": question.question_type,
                "baseline": base_metric.get("percentage", base_metric.get("average")),
                "endline": end_metric.get("percentage", end_metric.get("average")),
                "percentage": percentage,
                "average": average,
            }
        )
    return compare


def follow_up_summary(programme):
    result = []
    for s in programme.surveys.filter(survey_type=Survey.SurveyType.FOLLOW_UP):
        result.append(survey_results(s))
    return result


def organisation_summary(organisation):
    programme_summaries = []
    totals = {"participants_reached": 0, "active": 0, "completed": 0, "dropped_out": 0}
    survey_completions = []
    for p in organisation.programmes.all():
        summary = programme_summary(p)
        for key in totals:
            totals[key] += summary[key]
        programme_summaries.append(summary)
        for s in p.surveys.all():
            assigned = s.assignments.exclude(participant__isnull=True).count()
            submitted = s.responses.filter(submitted=True).count()
            survey_completions.append(
                {
                    "survey": s.id,
                    "title": s.title,
                    "survey_type": s.survey_type,
                    "programme": p.id,
                    "assigned": assigned,
                    "submitted": submitted,
                    "completion_rate": round((submitted / assigned) * 100, 1) if assigned else 0.0,
                }
            )
    return {
        "organisation": organisation.id,
        "name": organisation.name,
        "programmes_count": len(programme_summaries),
        "totals": totals,
        "programmes": programme_summaries,
        "survey_completions": survey_completions,
    }


def programme_dashboard(programme):
    """Full dashboard payload designed for React chart components."""
    return {
        "summary": programme_summary(programme),
        "kpis": kpi_performance(programme),
        "surveys": [survey_results(s) for s in programme.surveys.all()],
        "baseline_vs_endline": baseline_endline_compare(programme),
        "follow_up": follow_up_summary(programme),
        "challenges": challenge_analytics(programme),
    }


def challenge_analytics(programme=None):
    challenges = Challenge.objects.all()
    if programme:
        challenges = challenges.filter(programme=programme)

    total = challenges.count()
    open_count = challenges.filter(
        status__in=[Challenge.Status.OPEN, Challenge.Status.IN_PROGRESS]
    ).count()
    resolved_count = challenges.filter(status=Challenge.Status.RESOLVED).count()

    return {
        "total": total,
        "open": open_count,
        "resolved": resolved_count,
        "resolution_rate": round((resolved_count / total) * 100, 1) if total else 0.0,
        "by_category": list(
            challenges.values("category").annotate(count=Count("id")).order_by("-count")
        ),
        "by_status": list(challenges.values("status").annotate(count=Count("id")).order_by()),
    }