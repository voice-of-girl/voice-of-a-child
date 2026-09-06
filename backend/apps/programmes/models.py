"""Programme model."""
from django.db import models

from apps.core.models import OrganisationScopedModel


class Programme(OrganisationScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        PAUSED = "PAUSED", "Paused"
        COMPLETED = "COMPLETED", "Completed"
        CLOSED = "CLOSED", "Closed"

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    target_participants = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "status"]),
            models.Index(fields=["organisation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.organisation.name})"

    def surveys_related_response_count(self):
        """Total submitted survey responses attached to this programme."""
        from apps.surveys.models import SurveyResponse

        return SurveyResponse.objects.filter(programme=self, status=SurveyResponse.Status.SUBMITTED).count()