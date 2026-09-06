from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, user_is_organisation
from apps.organisations.models import Organisation
from apps.organisations.serializers import (
    OrganisationSerializer,
    OrganisationStatusSerializer,
)


class OrganisationViewSet(viewsets.ModelViewSet):
    """Admin full CRUD; organisation users see (only) their own organisation."""

    queryset = Organisation.objects.prefetch_related("users").order_by("-created_at")
    serializer_class = OrganisationSerializer
    permission_classes = [IsAdmin]
    search_fields = ["name", "email", "contact_person", "district", "country"]
    filterset_fields = ["status", "organisation_type", "district", "country"]

    def get_queryset(self):
        if user_is_organisation(self.request.user):
            return self.queryset.filter(id=self.request.user.organisation_id)
        return self.queryset

    def get_permissions(self):
        # Organisation users may read their own organisation profile only.
        if self.action in ("list", "retrieve"):
            return []
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        org = serializer.save()
        # The admin creating the organisation may optionally belong to it.
        org.save()

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        org = self.get_object()
        org.status = Organisation.Status.ACTIVE
        org.save()
        return Response(OrganisationSerializer(org).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        org = self.get_object()
        org.status = Organisation.Status.INACTIVE
        org.save()
        return Response(OrganisationSerializer(org).data)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        org = self.get_object()
        org.status = Organisation.Status.SUSPENDED
        org.save()
        return Response(OrganisationSerializer(org).data)

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        org = self.get_object()
        serializer = OrganisationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org.status = serializer.validated_data["status"]
        org.save()
        return Response(OrganisationSerializer(org).data)


class MyOrganisationViewSet(viewsets.ViewSet):
    """Authenticated org user views own organisation profile."""

    def list(self, request):
        if not user_is_organisation(request.user):
            return Response(
                {"detail": "Only organisation users have an organisation."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        org = Organisation.objects.get(id=request.user.organisation_id)
        return Response(OrganisationSerializer(org).data)