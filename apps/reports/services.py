"""Structured report-data generation and exports.

Prioritises reliable JSON report data plus CSV and XLSX exports.
"""
import csv
import io
from datetime import datetime

from apps.analytics.services import (
    baseline_endline_compare,
    challenge_analytics,
    follow_up_summary,
    kpi_performance,
    programme_summary,
    survey_results,
)


def build_programme_report(programme):
    """Assemble a complete structured programme report."""
    summary = programme_summary(programme)
    compare = baseline_endline_compare(programme)
    challenges = challenge_analytics(programme)
    follow_up = follow_up_summary(programme)

    top_challenges = challenges.get("by_category", [])[:3]
    recommendations = []
    if summary.get("dropout_rate", 0) > 15:
        recommendations.append(
            "Explore retention strategies: dropout rate exceeds 15%."
        )
    for item in top_challenges:
        recommendations.append(
            f"Prioritise resolving the common '{item['category']}' challenge "
            f"(reported {item['count']} times)."
        )
    unresolved = challenges.get("open", 0)
    if unresolved:
        recommendations.append(
            f"{unresolved} challenges are still open - schedule follow-up actions."
        )
    if not compare:
        recommendations.append(
            "Add baseline and endline surveys to enable impact comparison."
        )

    return {
        "meta": {
            "report_type": "programme",
            "programme": programme.id,
            "title": programme.title,
            "organisation": programme.organisation.name,
            "status": programme.status,
            "generated_at": datetime.now().isoformat(),
        },
        "overview": {
            "description": programme.description,
            "category": programme.category,
            "location": programme.location,
            "start_date": programme.start_date.isoformat() if programme.start_date else None,
            "end_date": programme.end_date.isoformat() if programme.end_date else None,
            "target_participants": programme.target_participants,
        },
        "objectives": [o.title for o in programme.objectives.all()],
        "participants": summary,
        "kpi_performance": kpi_performance(programme),
        "survey_findings": [survey_results(s) for s in programme.surveys.all()],
        "challenges": challenges,
        "outcomes": {
            "baseline_vs_endline": compare,
            "follow_up": follow_up,
        },
        "recommendations": recommendations,
    }
def programme_participants_csv(programme):
    """CSV export of participants enrolled in a programme."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Full Name",
            "Phone",
            "Email",
            "District",
            "Education Level",
            "Employment Status",
            "Programme Status",
            "Progress %",
            "Enrolled At",
            "Completed At",
        ]
    )
    enrollments = programme.enrollments.select_related("participant").order_by(
        "participant__full_name"
    )
    for e in enrollments:
        p = e.participant
        writer.writerow(
            [
                p.full_name,
                p.phone_number or "",
                p.email or "",
                p.district or "",
                p.get_education_level_display(),
                p.get_employment_status_display(),
                e.get_status_display(),
                e.progress,
                e.enrolled_at.isoformat(),
                e.completed_at.isoformat() if e.completed_at else "",
            ]
        )
    buffer.seek(0)
    return buffer.getvalue()


def survey_responses_csv(survey):
    """Flattened CSV export of a survey's submitted responses."""
    buffer = io.StringIO()
    questions = list(survey.questions.all())
    writer = csv.writer(buffer)
    writer.writerow(
        ["Response ID", "Participant", "Submitted At"]
        + [q.question_text for q in questions]
    )
    responses = survey.responses.filter(submitted=True).prefetch_related("answers")
    for r in responses:
        by_question = {a.question_id: a.value for a in r.answers.all()}
        row = [
            r.id,
            r.participant.full_name if r.participant else "Anonymous",
            r.submitted_at.isoformat() if r.submitted_at else "",
        ]
        for q in questions:
            value = by_question.get(q.id)
            if isinstance(value, list):
                value = "; ".join(map(str, value))
            row.append(value if value is not None else "")
        writer.writerow(row)
    buffer.seek(0)
    return buffer.getvalue()