from django.db import models
from django.conf import settings

class Organisation(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    class OrgType(models.TextChoices):
        NGO = 'NGO', 'Non-Governmental Organisation'
        FOUNDATION = 'FOUNDATION', 'Foundation / Philanthropy'
        TRAINING_INSTITUTE = 'TRAINING_INSTITUTE', 'Vocational / Training Institution'
        EMPLOYER = 'EMPLOYER', 'Employer / Enterprise'
        GOVERNMENT = 'GOVERNMENT', 'Government Initiative'
        COMMUNITY_BASED = 'COMMUNITY_BASED', 'Community Based Organisation'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organisation_type = models.CharField(max_length=50, choices=OrgType.choices, default=OrgType.NGO)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Uganda')
    verification_status = models.CharField(
        max_length=20, 
        choices=VerificationStatus.choices, 
        default=VerificationStatus.PENDING
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='organisations',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
