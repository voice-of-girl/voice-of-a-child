import datetime

from django.db import models

from apps.organisations.models import Organisation, OrganisationScopedModel


class Participant(OrganisationScopedModel):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    class Gender(models.TextChoices):
        FEMALE = "FEMALE", "Female"
        MALE = "MALE", "Male"
        OTHER = "OTHER", "Other"

    class EducationLevel(models.TextChoices):
        NONE = "NONE", "No Formal Education"
        PRIMARY = "PRIMARY", "Primary Education"
        SECONDARY_O_LEVEL = "SECONDARY_O_LEVEL", "Secondary (O-Level)"
        SECONDARY_A_LEVEL = "SECONDARY_A_LEVEL", "Secondary (A-Level)"
        VOCATIONAL = "VOCATIONAL", "Vocational / Certificate"
        DIPLOMA = "DIPLOMA", "Diploma"
        BACHELORS = "BACHELORS", "Bachelors Degree"
        POSTGRADUATE = "POSTGRADUATE", "Postgraduate"
        OTHER = "OTHER", "Other / Informal"

    class EmploymentStatus(models.TextChoices):
        UNEMPLOYED = "UNEMPLOYED", "Unemployed"
        STUDENT = "STUDENT", "Student"
        SELF_EMPLOYED = "SELF_EMPLOYED", "Self-Employed / Entrepreneur"
        PART_TIME = "PART_TIME", "Part-time Employment"
        FULL_TIME = "FULL_TIME", "Full-time Employment"
        INTERN = "INTERN", "Intern / Apprentice"

    # Public registrations are org-agnostic until claimed by an organisation.
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="participants",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.FEMALE)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Uganda")
    education_level = models.CharField(
        max_length=30,
        choices=EducationLevel.choices,
        default=EducationLevel.SECONDARY_O_LEVEL,
    )
    skills = models.JSONField(default=list, blank=True)
    interests = models.JSONField(default=list, blank=True)
    career_goals = models.TextField(blank=True)
    employment_status = models.CharField(
        max_length=30,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.UNEMPLOYED,
    )
    registration_source = models.CharField(max_length=100, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.district or 'N/A'})"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = datetime.date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )
