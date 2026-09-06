"""Programme views with strict organisation scoping."""
from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import (
    CanAdminTenantData,
    CanWriteTenantData,
)
from apps.core.services import audit
from apps.participants.models import Participant
from apps.participants.serializers import ParticipantSerializer

from .models import Programme
from .serializers import ProgrammeSerializer


class ProgrammeViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ProgrammeSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [CanAdminTenantData()]
        if self.action in ("create", "update", "partial_update"):
            return [CanWriteTenantData()]
        return [CanWriteTenantData()]

    def get_queryset(self):
        qs = Programme.objects.select_related("organisation").annotate(
            participant_count=Count("participants", distinct=True)
        )
        return qs

    def perform_create(self, serializer):
        programme = serializer.save(organisation=self.request.user.organisation)
        audit(self.request.user, "programme.create", programme.name)

    def perform_update(self, serializer):
        programme = serializer.save()
        audit(self.request.user, "programme.update", programme.name)

    def perform_destroy(self, instance):
        audit(self.request.user, "programme.delete", instance.name)
        instance.delete()

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, pk=None):
        """Aggregated programme statistics optimised for the dashboard."""
        programme = self.get_object()
        participants = programme.participants.all()
        total = participants.count()
        completed = participants.filter(status=Participant.Status.COMPLETED).count()
        active = participants.filter(status=Participant.Status.ACTIVE).count()
        responses = programme.surveys_related_response_count()
        return Response(
            {
                "programme_id": str(programme.id),
                "programme": programme.name,
                "enrolment": total,
                "active": active,
                "completed": completed,
                "completion_rate": round((completed / total * 100), 1) if total else 0.0,
                "survey_responses": responses,
                "target_participants": programme.target_participants,
            }
        )

    @action(detail=True, methods=["get", "post"])
    def participants(self, request, pk=None):
        """List or add participants for this programme (nested resource)."""
        programme = self.get_object()
        if request.method == "GET":
            qs = programme.participants.select_related("organisation").order_by("-created_at")
            page = self.paginate_queryset(qs)
            serializer = ParticipantSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ParticipantSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        participant = serializer.save(
            organisation=request.user.organisation,
            programme=programme,
        )
        audit(request.user, "programme.add_participant", participant.id)
        return Response(ParticipantSerializer(participant).data, status=201)