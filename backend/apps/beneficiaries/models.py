from django.db import models
from django.conf import settings

class BeneficiaryProfile(models.Model):
    class EducationLevel(models.TextChoices):
        PRIMARY = 'PRIMARY', 'Primary Education'
        SECONDARY_O_LEVEL = 'SECONDARY_O_LEVEL', 'Secondary (O-Level)'
        SECONDARY_A_LEVEL = 'SECONDARY_A_LEVEL', 'Secondary (A-Level)'
        VOCATIONAL_CERTIFICATE = 'VOCATIONAL_CERTIFICATE', 'Vocational / Certificate'
        DIPLOMA = 'DIPLOMA', 'Diploma'
        BACHELORS = 'BACHELORS', 'Bachelors Degree'
        POSTGRADUATE = 'POSTGRADUATE', 'Postgraduate / Masters'
        OTHER = 'OTHER', 'Other / Informal'

    class EmploymentStatus(models.TextChoices):
        UNEMPLOYED = 'UNEMPLOYED', 'Unemployed'
        STUDENT = 'STUDENT', 'Full-time Student'
        SELF_EMPLOYED = 'SELF_EMPLOYED', 'Self-Employed / Entrepreneur'
        PART_TIME = 'PART_TIME', 'Part-time Employed'
        FULL_TIME = 'FULL_TIME', 'Full-time Employed'
        INTERN = 'INTERN', 'Intern / Apprentice'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='beneficiary_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, default='Female')
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Uganda')
    
    education_level = models.CharField(
        max_length=50,
        choices=EducationLevel.choices,
        default=EducationLevel.SECONDARY_O_LEVEL
    )
    school_or_institution = models.CharField(max_length=255, blank=True)
    employment_status = models.CharField(
        max_length=50,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.UNEMPLOYED
    )
    career_goals = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    
    skills = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Beneficiary: {self.user.email} - {self.district}"
