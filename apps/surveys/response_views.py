from rest_framework import viewsets

from apps.accounts.permissions import IsAdminOrOrganisationUser
from apps.surveys.models import SurveyResponse
from apps.surveys.serializers import SurveyResponseSerializer


class SurveyResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to survey responses (org-scoped)."""

    queryset = SurveyResponse.objects.select_related(
        "survey", "participant", "organisation"
    ).order_by("-created_at")
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsAdminOrOrganisationUser]
    filterset_fields = ["survey", "participant", "organisation", "submitted"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "ADMIN":
            return qs
        return qs.filter(organisation_id=self.request.user.organisation_id)