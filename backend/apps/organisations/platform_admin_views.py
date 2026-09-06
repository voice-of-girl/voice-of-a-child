"""Platform admin endpoints mounted at /api/admin/."""
import secrets

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from apps.accounts.serializers import UserSerializer
from apps.core.permissions import IsPlatformAdmin
from apps.core.services import audit
from apps.organisations.serializers import OrganisationSerializer

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsPlatformAdmin])
def system_overview(request):
    """Aggregated system-wide statistics for the platform admin dashboard."""
    from apps.impact.models import ImpactProject
    from apps.monitoring.models import Challenge
    from apps.participants.models import Participant
    from apps.programmes.models import Programme
    from apps.surveys.models import Survey, SurveyResponse

    data = {
        "organisations": {"total": request.user.organisations_visible().count()},
        "users": User.objects.count(),
        "programmes": Programme.objects.count(),
        "participants": Participant.objects.count(),
        "surveys": Survey.objects.count(),
        "responses": SurveyResponse.objects.count(),
        "challenges": Challenge.objects.count(),
        "impact_projects": ImpactProject.objects.count(),
        "organisations_by_status": list(
            request.user.organisations_visible()
            .values_list("verification_status")
            .annotate(count=Count("id"))
        ),
    }
    return Response(data)


class PlatformOrganisationListCreateView(ListCreateAPIView):
    """GET/POST /api/admin/organisations/ — list and create organisations."""

    permission_classes = [IsPlatformAdmin]
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        return self.request.user.organisations_visible()

    def perform_create(self, serializer):
        org = serializer.save()
        audit(self.request.user, "organisation.create", org.name)


class PlatformOrganisationDetailView(RetrieveUpdateAPIView):
    """GET/PATCH /api/admin/organisations/{id}/ — manage one organisation."""

    permission_classes = [IsPlatformAdmin]
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        return self.request.user.organisations_visible()

    def perform_update(self, serializer):
        org = serializer.save()
        audit(self.request.user, "organisation.update", org.name)


class PlatformOrgAdminAccountView(APIView):
    pass  # replaced below (kept for import safety during edits)



class PlatformUserListView(ListAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().select_related("organisation")