from django.db import models


class Organisation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        SUSPENDED = "SUSPENDED", "Suspended"

    class OrgType(models.TextChoices):
        NGO = "NGO", "Non-Governmental Organisation"
        FOUNDATION = "FOUNDATION", "Foundation"
        SCHOOL = "SCHOOL", "School / Training Institution"
        CORPORATE = "CORPORATE", "Corporate / CSR"
        COMMUNITY_BASED = "COMMUNITY_BASED", "Community Based Organisation"
        GOVERNMENT = "GOVERNMENT", "Government"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=255)
    organisation_type = models.CharField(
        max_length=30, choices=OrgType.choices, default=OrgType.NGO
    )
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Uganda")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class OrganisationScopedModel(models.Model):
    """Abstract base for every record owned by an organisation.

    Guarantees that data can always be isolated at the organisation level.
    """

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True

    def get_organisation_id(self):
        return self.organisation_id
