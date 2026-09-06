"""Shared abstract models used across the platform."""
import uuid

from django.db import models


class UUIDModel(models.Model):
    """Base model using a UUID primary key (no enumerable database ids)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrganisationScopedModel(UUIDModel, TimeStampedModel):
    """
    Every tenant-owned model inherits from this base class.

    ``organisation`` is the tenant key. All queries MUST be filtered by it;
    the view layer enforces this automatically (see ``TenantQuerysetMixin``).
    """

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True