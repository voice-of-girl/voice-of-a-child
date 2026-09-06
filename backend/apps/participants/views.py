"""Participant views (organisation-scoped)."""
from django.db.models import Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import CanAdminTenantData, CanWriteTenantData
from apps.core.services import audit
from apps.programmes.models import Programme

from .models import Participant
from .serializers import ParticipantBulkImportSerializer, ParticipantSerializer


class ParticipantViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ParticipantSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone", "external_reference", "location"]
    ordering_fields = ["created_at", "name", "status", "age"]

    def get_permissions(self):
        if self.action == "destroy":
            return [CanAdminTenantData()]
        return [CanWriteTenantData()]

    def get_queryset(self):
        qs = Participant.objects.select_related("organisation", "programme")
        programme = self.request.query_params.get("programme")
        status_filter = self.request.query_params.get("status")
        if programme:
            qs = qs.filter(programme_id=programme)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        participant = serializer.save(organisation=self.request.user.organisation)
        audit(self.request.user, "participant.create", participant.name)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        audit(self.request.user, "participant.delete", instance.name)
        instance.delete()

    @action(detail=False, methods=["post"], url_path="import")
    def import_batch(self, request):
        """Bulk import participants. Upserts by external_reference (when given)."""
        rows = request.data.get("participants", [])
        if not isinstance(rows, list) or not rows:
            return Response({"detail": "Provide a list under 'participants'."}, status=400)
        programme = Programme.objects.filter(
            id=request.data.get("programme_id"), organisation=request.user.organisation
        ).first()

        created, updated, skipped = 0, 0, 0
        # Whitelist: never allow the client to set organisation, id or timestamps.
        allowed = {
            "name", "email", "phone", "external_reference", "gender",
            "date_of_birth", "age", "location", "district", "status",
            "enrolled_date",
        }
        for row in rows:
            if not isinstance(row, dict):
                skipped += 1
                continue
            row = {k: v for k, v in row.items() if k in allowed and v not in (None, "")}
            ref = (row.get("external_reference") or "").strip()
            email = (row.get("email") or "").strip().lower()
            existing = None
            if ref:
                existing = Participant.objects.filter(
                    organisation=request.user.organisation, external_reference=ref
                ).first()
            if existing is None and email:
                existing = Participant.objects.filter(
                    organisation=request.user.organisation, email=email
                ).first()
            if existing:
                for key, value in row.items():
                    setattr(existing, key, value)
                if programme:
                    existing.programme = programme
                existing.save()
                updated += 1
            else:
                Participant.objects.create(
                    organisation=request.user.organisation,
                    programme=programme,
                    **row,
                )
                created += 1
        audit(request.user, "participant.import", f"created={created} updated={updated}")
        return Response({"created": created, "updated": updated, "skipped": skipped})