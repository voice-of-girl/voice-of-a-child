"""Survey, question, response and answer models."""
import enum
import secrets

from django.conf import settings
from django.db import models

from apps.core.models import OrganisationScopedModel, TimeStampedModel, UUIDModel


def generate_public_token():
    """Cryptographically secure unguessable token for public survey links."""
    return secrets.token_urlsafe(32)


class Survey(OrganisationScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CLOSED = "CLOSED", "Closed"

    class Stage(models.TextChoices):
        BASELINE = "BASELINE", "Baseline"
        MIDLINE = "MIDLINE", "Midline / Monitoring"
        ENDLINE = "ENDLINE", "Endline"
        FOLLOW_UP = "FOLLOW_UP", "Follow-up"
        CUSTOM = "CUSTOM", "Custom"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surveys",
        db_index=True,
    )
    impact_project = models.ForeignKey(
        "impact.ImpactProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="surveys",
        db_index=True,
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.BASELINE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    public_token = models.CharField(
        max_length=64, unique=True, db_index=True, default=generate_public_token
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    allow_multiple_responses = models.BooleanField(
        default=False, help_text="Allow more than one response per person."
    )
    thank_you_message = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_surveys",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "status"]),
            models.Index(fields=["organisation", "programme"]),
            models.Index(fields=["organisation", "public_token"]),
        ]

    def __str__(self):
        return self.title

    def is_accepting_responses(self):
        """A survey accepts responses only while published and in window."""
        from django.utils import timezone

        if self.status != self.Status.PUBLISHED:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class SurveyQuestion(TimeStampedModel, UUIDModel):
    class QuestionType(models.TextChoices):
        SHORT_TEXT = "SHORT_TEXT", "Short Text"
        LONG_TEXT = "LONG_TEXT", "Long Text"
        NUMBER = "NUMBER", "Number"
        MULTIPLE_CHOICE = "MULTIPLE_CHOICE", "Multiple Choice"
        CHECKBOX = "CHECKBOX", "Checkboxes"
        DROPDOWN = "DROPDOWN", "Dropdown"
        YES_NO = "YES_NO", "Yes / No"
        RATING_SCALE = "RATING_SCALE", "Rating Scale (1-5)"
        DATE = "DATE", "Date"

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    question = models.CharField(max_length=500)
    help_text = models.CharField(max_length=300, blank=True)
    question_type = models.CharField(max_length=30, choices=QuestionType.choices)
    options = models.JSONField(default=list, blank=True)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    validation_rules = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["order", "created_at"]
        unique_together = [("survey", "order")]

    def __str__(self):
        return f"{self.survey.title} :: Q{self.order}"


class SurveyResponse(OrganisationScopedModel):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="responses", db_index=True
    )
    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
        db_index=True,
    )
    participant = models.ForeignKey(
        "participants.Participant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
        db_index=True,
    )
    impact_project = models.ForeignKey(
        "impact.ImpactProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
        db_index=True,
    )
    respondent_name = models.CharField(max_length=255, blank=True)
    respondent_email = models.EmailField(blank=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUBMITTED, db_index=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["organisation", "survey", "submitted_at"]),
            models.Index(fields=["organisation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.survey.title} response {self.id}"


class SurveyAnswer(TimeStampedModel, UUIDModel):
    response = models.ForeignKey(
        SurveyResponse, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        SurveyQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    value = models.JSONField()

    class Meta:
        unique_together = [("response", "question")]

    def __str__(self):
        return f"{self.response_id} -> {self.question_id}: {self.value}"


class QuestionTypeMeta(enum.Enum):
    """Shared question-type metadata used by validators and the frontend."""

    MULTI = "multi"  # multiple selection (checkbox)
    SINGLE = "single"  # single selection
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"

    @classmethod
    def kind(cls, qtype):
        if qtype in {SurveyQuestion.QuestionType.CHECKBOX}:
            return cls.MULTI
        if qtype in {
            SurveyQuestion.QuestionType.MULTIPLE_CHOICE,
            SurveyQuestion.QuestionType.DROPDOWN,
            SurveyQuestion.QuestionType.YES_NO,
        }:
            return cls.SINGLE
        if qtype in {SurveyQuestion.QuestionType.NUMBER}:
            return cls.NUMBER
        if qtype == SurveyQuestion.QuestionType.DATE:
            return cls.DATE
        return cls.TEXT