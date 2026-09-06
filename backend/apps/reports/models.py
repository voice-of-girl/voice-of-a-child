"""Report model."""
from django.conf import settings
from django.db import models

from apps.core.models import OrganisationScopedModel


class Report(OrganisationScopedModel):
    class ReportType(models.TextChoices):
        GENERAL = "GENERAL", "General Impact Report"
        PROGRAMME = "PROGRAMME", "Programme Report"
        SURVEY = "SURVEY", "Survey Report"
        IMPACT = "IMPACT", "Impact Report"
        KPI = "KPI", "KPI Report"
        PROJECT = "PROJECT", "Impact Project Report"

    class Status(models.TextChoices):
        GENERATING = "GENERATING", "Generating"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    class FileFormat(models.TextChoices):
        PDF = "PDF", "PDF"
        EXCEL = "EXCEL", "Excel"
        CSV = "CSV", "CSV"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    impact_project = models.ForeignKey(
        "impact.ImpactProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    report_type = models.CharField(max_length=30, choices=ReportType.choices, default=ReportType.GENERAL)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.GENERATING, db_index=True)
    file_format = models.CharField(max_length=10, choices=FileFormat.choices, default=FileFormat.PDF)
    parameters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="reports/%Y/%m/", blank=True, null=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_reports",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organisation", "status"])]

    def __str__(self):
        return f"{self.title} ({self.report_type}/{self.file_format})"

    @property
    def filename(self):
        safe_title = "".join(c for c in self.title if c.isalnum() or c in " -_").strip().replace(" ", "_")
        return f"{safe_title}.{self.file_format.lower()}"