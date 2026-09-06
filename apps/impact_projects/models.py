import secrets
from datetime import date

from django.conf import settings
from django.db import models

from apps.organisations.models import Organisation


def generate_access_token():
    return secrets.token_urlsafe(32)


class ImpactProject(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    client_organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="impact_projects",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    target_respondents = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_impact_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.client_organisation.name})"

    @property
    def client_name(self):
        return self.client_organisation.name


class ImpactSurvey(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CLOSED = "CLOSED", "Closed"

    class SurveyType(models.TextChoices):
        BASELINE = "BASELINE", "Baseline"
        ENDLINE = "ENDLINE", "Endline"
        FOLLOW_UP = "FOLLOW_UP", "Follow-up"
        CUSTOM = "CUSTOM", "Custom"

    project = models.ForeignKey(ImpactProject, on_delete=models.CASCADE, related_name="surveys")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    survey_type = models.CharField(
        max_length=20, choices=SurveyType.choices, default=SurveyType.BASELINE
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    # Flexible question definition stored as JSON - keeps standalone service decoupled.
    questions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_survey_type_display()})"


class ImpactResponse(models.Model):
    survey = models.ForeignKey(ImpactSurvey, on_delete=models.CASCADE, related_name="responses")
    access_token = models.CharField(
        max_length=64, unique=True, default=generate_access_token, editable=False
    )
    respondent_name = models.CharField(max_length=255, blank=True)
    respondent_phone = models.CharField(max_length=50, blank=True)
    answers = models.JSONField(default=list, blank=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Impact response to {self.survey.title} ({'submitted' if self.submitted else 'pending'})"
