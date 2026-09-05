from django.db import models
from django.conf import settings
from apps.programmes.models import Programme

class VerificationTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        IN_PROGRESS = 'IN_PROGRESS', 'Field Visit In Progress'
        VERIFIED = 'VERIFIED', 'Verified / Confirmed'
        FLAGGED = 'FLAGGED', 'Flagged for Admin Review'
        REJECTED = 'REJECTED', 'Information Inaccurate'

    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_verifications'
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_tasks'
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='verification_tasks'
    )
    task_type = models.CharField(max_length=100, default='IDENTITY_AND_LOCATION')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    home_visit_conducted = models.BooleanField(default=False)
    id_documents_checked = models.BooleanField(default=False)
    guardian_contacted = models.BooleanField(default=False)
    
    field_notes = models.TextField(blank=True)
    gps_latitude = models.FloatField(null=True, blank=True)
    gps_longitude = models.FloatField(null=True, blank=True)
    
    scheduled_for = models.DateField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task: Verify {self.beneficiary.email} by {self.assigned_officer.email} ({self.status})"
