from django.db import models
from django.conf import settings
from apps.programmes.models import Programme

class BeneficiaryParticipation(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'REGISTERED', 'Registered'
        SELECTED = 'SELECTED', 'Selected'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        DROPPED_OUT = 'DROPPED_OUT', 'Dropped Out'

    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='participations'
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    participation_status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.REGISTERED
    )
    attendance_rate = models.FloatField(default=0.0)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    outcome_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('beneficiary', 'programme')

    def __str__(self):
        return f"{self.beneficiary.email} in {self.programme.title} ({self.participation_status})"
