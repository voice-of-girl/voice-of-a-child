from django.conf import settings
from django.db import models

from apps.organisations.models import OrganisationScopedModel
from apps.participants.models import Participant


class Programme(OrganisationScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    target_participants = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_programmes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ProgrammeObjective(models.Model):
    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, related_name="objectives"
    )
    title = models.CharField(max_length=255)
    detail = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.programme.title} - {self.title}"


class ProgrammeKPI(models.Model):
    class Category(models.TextChoices):
        INPUT = "INPUT", "Input"
        ACTIVITY = "ACTIVITY", "Activity"
        OUTPUT = "OUTPUT", "Output"
        OUTCOME = "OUTCOME", "Outcome"
        IMPACT = "IMPACT", "Impact"

    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, related_name="kpis"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OUTPUT
    )
    unit = models.CharField(max_length=50, default="participants")
    target_value = models.FloatField(default=0)
    current_value = models.FloatField(default=0)
    baseline_value = models.FloatField(default=0, help_text="Starting point for % change")
    measurement_frequency = models.CharField(max_length=50, default="Quarterly")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "id"]

    @property
    def progress_percentage(self):
        if self.target_value <= 0:
            return 0.0
        return min(100.0, round((self.current_value / self.target_value) * 100, 1))

    @property
    def percentage_change(self):
        """Percent change vs baseline (guarded against divide-by-zero)."""
        if self.baseline_value == 0:
            return 100.0 if self.current_value else 0.0
        return round(((self.current_value - self.baseline_value) / self.baseline_value) * 100, 1)

    @property
    def percentage_point_change(self):
        return round(self.current_value - self.baseline_value, 1)

    def __str__(self):
        return f"{self.name}: {self.current_value}/{self.target_value} {self.unit}"


class ProgrammeEnrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "Enrolled"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        DROPPED_OUT = "DROPPED_OUT", "Dropped Out"

    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, related_name="enrollments"
    )
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name="enrollments"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ENROLLED
    )
    progress = models.FloatField(default=0.0, help_text="0 - 100")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    outcome_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["programme", "participant"], name="unique_programme_participant"
            )
        ]

    def __str__(self):
        return f"{self.participant.full_name} in {self.programme.title} ({self.status})"
