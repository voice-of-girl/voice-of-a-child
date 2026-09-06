"""Impact models: KPIs, impact measurements and standalone impact projects."""
from django.conf import settings
from django.db import models

from apps.core.models import OrganisationScopedModel


class ImpactProject(OrganisationScopedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        ARCHIVED = "ARCHIVED", "Archived"

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_projects",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organisation", "status"])]

    def __str__(self):
        return self.name


class KPI(OrganisationScopedModel):
    class Status(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", "Not Started"
        ON_TRACK = "ON_TRACK", "On Track"
        AT_RISK = "AT_RISK", "At Risk"
        ACHIEVED = "ACHIEVED", "Achieved"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kpis",
        db_index=True,
    )
    impact_project = models.ForeignKey(
        ImpactProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kpis",
        db_index=True,
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=80, default="%")
    baseline = models.FloatField(null=True, blank=True)
    current_value = models.FloatField(default=0.0)
    target = models.FloatField(null=True, blank=True)
    endline = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOT_STARTED, db_index=True
    )
    trend_data = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["organisation", "programme"])]

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        """Progress from baseline towards target (clamped 0-100)."""
        if self.target is None or self.target == 0:
            return 0.0
        if self.baseline is not None and self.target != self.baseline:
            progress = (self.current_value - self.baseline) / (self.target - self.baseline) * 100
        else:
            progress = self.current_value / self.target * 100
        return round(max(0.0, min(100.0, progress)), 2)


class ImpactMeasurement(OrganisationScopedModel):
    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="impact_measurements",
    )
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="impact_measurements",
    )
    kpi = models.ForeignKey(
        KPI,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="measurements",
    )
    impact_project = models.ForeignKey(
        ImpactProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="impact_measurements",
    )
    metric = models.CharField(max_length=255)
    value = models.FloatField()
    period = models.DateField(db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-period"]
        indexes = [models.Index(fields=["organisation", "period"])]

    def __str__(self):
        return f"{self.metric}: {self.value} ({self.period})"