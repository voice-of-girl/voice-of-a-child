import secrets

from django.conf import settings
from django.db import models

from apps.organisations.models import OrganisationScopedModel
from apps.participants.models import Participant
from apps.programmes.models import Programme


def generate_access_token():
    return secrets.token_urlsafe(32)


class Survey(OrganisationScopedModel):
    class SurveyType(models.TextChoices):
        BASELINE = "BASELINE", "Baseline"
        MONITORING = "MONITORING", "Monitoring"
        ENDLINE = "ENDLINE", "Endline"
        FOLLOW_UP = "FOLLOW_UP", "Follow-up"
        CUSTOM = "CUSTOM", "Custom"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        UNPUBLISHED = "UNPUBLISHED", "Unpublished"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    survey_type = models.CharField(
        max_length=20, choices=SurveyType.choices, default=SurveyType.BASELINE
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surveys",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_surveys",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_survey_type_display()})"


class Question(models.Model):
    class QuestionType(models.TextChoices):
        SHORT_TEXT = "SHORT_TEXT", "Short Text"
        LONG_TEXT = "LONG_TEXT", "Long Text"
        NUMBER = "NUMBER", "Number"
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE", "Multiple Choice"
        CHECKBOX = "CHECKBOX", "Checkbox (multi-select)"
        DROPDOWN = "DROPDOWN", "Dropdown"
        YES_NO = "YES_NO", "Yes / No"
        RATING = "RATING", "Rating"
        DATE = "DATE", "Date"

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=500)
    help_text = models.CharField(max_length=255, blank=True)
    question_type = models.CharField(max_length=30, choices=QuestionType.choices)
    required = models.BooleanField(default=True)
    options = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order}: {self.question_text}"


class SurveyAssignment(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="assignments")
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="survey_assignments",
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="survey_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["survey", "participant"], name="unique_survey_participant_assignment"
            )
        ]

    def __str__(self):
        return f"{self.survey.title} -> {self.participant or self.programme}"


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="survey_responses",
    )
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="survey_responses",
    )
    access_token = models.CharField(
        max_length=64, unique=True, default=generate_access_token, editable=False
    )
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Response to {self.survey.title} ({'submitted' if self.submitted else 'pending'})"


class Answer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    value = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["response", "question"], name="unique_response_question")
        ]

    def __str__(self):
        return f"Ans to Q{self.question_id}: {self.value}"
