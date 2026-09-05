from django.db import models
from apps.organisations.models import Organisation

class Programme(models.Model):
    class ProgrammeType(models.TextChoices):
        NEW_PROGRAMME = 'NEW_PROGRAMME', 'New Programme'
        EXISTING_PROGRAMME = 'EXISTING_PROGRAMME', 'Existing / Ongoing Programme'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active'
        PAUSED = 'PAUSED', 'Paused'
        COMPLETED = 'COMPLETED', 'Completed'
        CLOSED = 'CLOSED', 'Closed'

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='programmes'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100) # e.g. STEM, Vocational, Entrepreneurship, Health & Rights
    programme_type = models.CharField(
        max_length=30,
        choices=ProgrammeType.choices,
        default=ProgrammeType.NEW_PROGRAMME
    )
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    target_beneficiaries = models.PositiveIntegerField(default=100)
    
    # Matching criteria rule configuration
    criteria_education = models.JSONField(default=list, blank=True)
    criteria_skills = models.JSONField(default=list, blank=True)
    criteria_locations = models.JSONField(default=list, blank=True)
    criteria_min_age = models.IntegerField(default=15)
    criteria_max_age = models.IntegerField(default=28)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.organisation.name})"
