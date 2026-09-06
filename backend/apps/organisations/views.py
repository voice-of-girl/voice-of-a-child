"""Organisation views.

Tenant isolation: ordinary users only ever see their own organisation; the
platform admin can see and manage all organisations.
"""
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import (
    IsOrgAdminOrPlatformAdmin,
    IsPlatformAdmin,
    ensure_organisation_access,
)
from apps.core.services import audit

from .models import Organisation
from .serializers import OrganisationSerializer


class OrganisationViewSet(viewsets.ModelViewSet):
    """
    Manage organisations.

    - Platform admins: full CRUD over every organisation.
    - Organisation users: read-only access to their own organisation.
    """

    serializer_class = OrganisationSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsOrgAdminOrPlatformAdmin()]
        return [IsOrgAdminOrPlatformAdmin()]

    def get_queryset(self):
        user = self.request.user
        qs = user.organisations_visible()
        return qs.annotate(
            programmes_count=Count("programme_set", distinct=True),
            participants_count=Count("participant_set", distinct=True),
            surveys_count=Count("survey_set", distinct=True),
        )

    def perform_create(self, serializer):
        org = serializer.save()
        audit(self.request.user, "organisation.create", org.name)

    def perform_update(self, serializer):
        org = serializer.save()
        audit(self.request.user, "organisation.update", org.name)

    def perform_destroy(self, instance):
        audit(self.request.user, "organisation.delete", instance.name)
        instance.delete()

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Platform admin action: set verification_status."""
        org = self.get_object()
        status_value = request.data.get("verification_status")
        if status_value not in dict(Organisation.VerificationStatus.choices):
            return Response(
                {"detail": "Invalid verification_status."}, status=400
            )
        org.verification_status = status_value
        org.save(update_fields=["verification_status"])
        audit(request.user, "organisation.verify", f"{org.name} -> {status_value}")
        return Response(OrganisationSerializer(org).data)