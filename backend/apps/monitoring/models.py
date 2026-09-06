"""Monitoring models: Challenges, Feedback and Support Requests."""
from django.conf import settings
from django.db import models

from apps.core.models import OrganisationScopedModel


class Challenge(OrganisationScopedModel):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Category(models.TextChoices):
        TRANSPORT = "TRANSPORT", "Transport"
        ATTENDANCE = "ATTENDANCE", "Attendance"
        EQUIPMENT = "EQUIPMENT", "Equipment / Materials"
        SCHEDULING = "SCHEDULING", "Scheduling"
        SAFETY = "SAFETY", "Safety"
        HEALTH = "HEALTH", "Health & Wellbeing"
        FAMILY_CARE = "FAMILY_CARE", "Family / Care"
        FINANCIAL = "FINANCIAL", "Financial"
        OTHER = "OTHER", "Other"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="challenges",
        db_index=True,
    )
    participant = models.ForeignKey(
        "participants.Participant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="challenges",
    )
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.OTHER, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_challenges",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "status"]),
            models.Index(fields=["organisation", "category"]),
            models.Index(fields=["organisation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.title} [{self.status}]"


class Feedback(OrganisationScopedModel):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        REVIEWED = "REVIEWED", "Reviewed"
        ACTIONED = "ACTIONED", "Actioned"

    class Category(models.TextChoices):
        PROGRAMME = "PROGRAMME", "Programme"
        FACILITATOR = "FACILITATOR", "Facilitator"
        MATERIALS = "MATERIALS", "Materials"
        VENUE = "VENUE", "Venue"
        GENERAL = "GENERAL", "General"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_items",
    )
    participant = models.ForeignKey(
        "participants.Participant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_items",
    )
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.GENERAL)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organisation", "status"])]

    def __str__(self):
        return f"{self.category}: {self.message[:60]}"


class SupportRequest(OrganisationScopedModel):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    class Category(models.TextChoices):
        TECHNICAL = "TECHNICAL", "Technical"
        DATA = "DATA", "Data / Records"
        MATERIALS = "MATERIALS", "Materials"
        TRAINING = "TRAINING", "Training"
        OTHER = "OTHER", "Other"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_requests",
    )
    participant = models.ForeignKey(
        "participants.Participant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_requests",
    )
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.OTHER)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_support_requests",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organisation", "status"])]

    def __str__(self):
        return f"{self.category}: {self.description[:60]}"