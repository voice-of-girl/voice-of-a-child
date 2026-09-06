"""Platform admin endpoints mounted at /api/admin/."""
import secrets

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import RegisterUserSerializer, UserSerializer
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
    """
    POST /api/admin/organisations/{id}/create-admin/

    Creates an Organisation Admin account for the given organisation.
    A secure password is generated when none is supplied and returned
    exactly once (it is never stored in plaintext or logged).
    """

    permission_classes = [IsPlatformAdmin]

    def post(self, request, pk):
        org = request.user.organisations_visible().filter(pk=pk).first()
        if org is None:
            return Response(
                {"detail": "Organisation not found."}, status=status.HTTP_404_NOT_FOUND
            )
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"email": ["Email is required."]}, status=400)
        first_name = (request.data.get("first_name") or "").strip()
        last_name = (request.data.get("last_name") or "").strip()
        password = request.data.get("password") or secrets.token_urlsafe(14)

        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"email": ["A user with this email already exists."]}, status=400
            )
        if len(password) < 8:
            return Response({"password": ["Minimum 8 characters."]}, status=400)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name or org.name,
            last_name=last_name or "Admin",
            role=User.Role.ORGANISATION_ADMIN,
            organisation=org,
        )
        audit(request.user, "organisation.create_admin", f"{user.email} @ {org.name}")
        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "organisation": str(org.id),
                "organisation_name": org.name,
                # Shown once so the platform admin can hand it over securely.
                "temporary_password": password,
            },
            status=status.HTTP_201_CREATED,
        )



class PlatformUserListView(ListCreateAPIView):
    """
    GET  /api/admin/users/ — list all platform users (filter by ?organisation= ?role=).
    POST /api/admin/users/ — provision a user with ANY role for ANY organisation.

    The platform admin is the sole creator of accounts. When no password is
    supplied a secure one is generated and returned once as
    ``temporary_password`` — it is never stored in plaintext or logged.
    """

    permission_classes = [IsPlatformAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.all().select_related("organisation")
        organisation = self.request.query_params.get("organisation")
        role = self.request.query_params.get("role")
        if organisation:
            qs = qs.filter(organisation_id=organisation)
        if role:
            qs = qs.filter(role=role)
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        generated_password = None
        if not data.get("password"):
            generated_password = secrets.token_urlsafe(14)
            data["password"] = generated_password

        serializer = RegisterUserSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        audit(request.user, "user.create", f"created user {user.email}")

        payload = UserSerializer(user, context={"request": request}).data
        if generated_password:
            payload["temporary_password"] = generated_password
        return Response(payload, status=status.HTTP_201_CREATED)