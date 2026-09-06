"""Organisation (tenant) model."""
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Organisation(UUIDModel, TimeStampedModel):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    class OrgType(models.TextChoices):
        NGO = "NGO", "Non-Governmental Organisation"
        FOUNDATION = "FOUNDATION", "Foundation / Philanthropy"
        TRAINING_INSTITUTE = "TRAINING_INSTITUTE", "Training Institution"
        SCHOOL = "SCHOOL", "School / Education"
        COMMUNITY = "COMMUNITY", "Community Organisation"
        GOVERNMENT = "GOVERNMENT", "Government"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    organisation_type = models.CharField(
        max_length=40, choices=OrgType.choices, default=OrgType.NGO
    )
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=100, default="Uganda")
    verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name