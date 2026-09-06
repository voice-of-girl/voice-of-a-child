from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminOrOrganisationUser
from apps.monitoring.models import Challenge
from apps.monitoring.serializers import (
    ChallengeResolveSerializer,
    ChallengeSerializer,
    ChallengeWriteSerializer,
)


class ChallengeViewSet(viewsets.ModelViewSet):
    """Challenges with filtering, resolve workflow and analytics."""

    queryset = Challenge.objects.select_related(
        "organisation", "programme", "participant"
    ).order_by("-date_reported")
    permission_classes = [IsAdminOrOrganisationUser]
    search_fields = ["description", "resolution_notes"]
    filterset_fields = ["category", "status", "programme", "participant", "organisation"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ChallengeWriteSerializer
        return ChallengeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organisation_id"] = self.request.user.organisation_id
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "ADMIN":
            return qs
        return qs.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        serializer.save(
            organisation_id=self.request.user.organisation_id,
            reported_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        challenge = self.get_object()
        self.check_object_permissions(request, challenge)
        serializer = ChallengeResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        challenge.status = Challenge.Status.RESOLVED
        challenge.date_resolved = timezone.now()
        challenge.resolution_notes = serializer.validated_data.get(
            "resolution_notes", challenge.resolution_notes
        )
        challenge.save()
        return Response(ChallengeSerializer(challenge).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        challenge = self.get_object()
        self.check_object_permissions(request, challenge)
        challenge.status = Challenge.Status.IN_PROGRESS
        challenge.save()
        return Response(ChallengeSerializer(challenge).data)