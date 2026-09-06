"""Platform admin endpoints mounted at /api/admin/."""
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.accounts.serializers import UserSerializer
from apps.core.permissions import IsPlatformAdmin
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


class PlatformOrganisationListView(ListAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = OrganisationSerializer

    def get_queryset(self):
        return self.request.user.organisations_visible()


class PlatformUserListView(ListAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().select_related("organisation")