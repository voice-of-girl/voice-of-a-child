"""Participant / respondent model."""
from django.db import models

from apps.core.models import OrganisationScopedModel


class Participant(OrganisationScopedModel):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Registered"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        DROPPED_OUT = "DROPPED_OUT", "Dropped Out"

    class Gender(models.TextChoices):
        FEMALE = "FEMALE", "Female"
        MALE = "MALE", "Male"
        NON_BINARY = "NON_BINARY", "Non-binary"
        OTHER = "OTHER", "Other"
        PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", "Prefer not to say"

    programme = models.ForeignKey(
        "programmes.Programme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="participants",
        db_index=True,
    )
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    phone = models.CharField(max_length=50, blank=True)
    external_reference = models.CharField(max_length=120, blank=True, db_index=True)

    gender = models.CharField(max_length=30, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=120, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REGISTERED, db_index=True
    )
    enrolled_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organisation", "status"]),
            models.Index(fields=["organisation", "programme"]),
            models.Index(fields=["organisation", "created_at"]),
        ]

    def __str__(self):
        return self.name