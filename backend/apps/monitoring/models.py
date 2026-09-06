from django.conf import settings
from django.db import models

from apps.organisations.models import OrganisationScopedModel
from apps.participants.models import Participant
from apps.programmes.models import Programme


class Challenge(OrganisationScopedModel):
    class Category(models.TextChoices):
        TRANSPORT = "TRANSPORT", "Transport"
        FINANCIAL = "FINANCIAL", "Financial"
        ATTENDANCE = "ATTENDANCE", "Attendance"
        MATERIALS = "MATERIALS", "Materials"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"

    programme = models.ForeignKey(
        Programme, on_delete=models.CASCADE, null=True, blank=True, related_name="challenges"
    )
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, null=True, blank=True, related_name="challenges"
    )
    category = models.CharField(max_length=30, choices=Category.choices)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    date_reported = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_challenges",
    )

    class Meta:
        ordering = ["-date_reported"]

    def __str__(self):
        return f"[{self.category}] {self.description[:50]} ({self.status})"
