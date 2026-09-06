"""Authentication and account views."""
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.permissions import IsPlatformAdmin
from apps.core.services import audit
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import Programme
from apps.surveys.models import Survey, SurveyResponse

from .serializers import (
    MeSerializer,
    PasswordChangeSerializer,
    RegisterUserSerializer,
    UserSerializer,
    VoiceTokenObtainPairSerializer,
)

User = get_user_model()


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ with {email, password}.

    Returns ``{access, refresh, user}`` where ``user`` is the serialized
    caller (role, organisation, etc.) so the frontend can route immediately
    without an extra ``/auth/me/`` round-trip.
    """

    serializer_class = VoiceTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class RefreshView(TokenRefreshView):
    """POST /api/auth/refresh/ with {refresh}."""


class LogoutView(APIView):
    """Blacklists the supplied refresh token."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()  # requires rest_framework_simplejwt.token_blacklist
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/me/ — current user's profile."""

    serializer_class = MeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        # Do not allow users to change role/org through this endpoint.
        serializer.save(role=self.request.user.role, organisation=self.request.user.organisation)


class RegisterUserView(generics.CreateAPIView):
    """POST /api/auth/register/ — create a user (platform/org admin only)."""

    serializer_class = RegisterUserSerializer
    permission_classes = (IsPlatformAdmin,)
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "default"

    def perform_create(self, serializer):
        user = serializer.save()
        audit(self.request.user, "user.create", f"created user {user.email}")


class PasswordChangeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        audit(user, "password.change")
        return Response({"detail": "Password updated."})


class DashboardView(APIView):
    """GET /api/auth/dashboard/ — role-scoped dashboard summary."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        role = user.role
        org = user.organisation

        if role == CustomUser.Role.PLATFORM_ADMIN:
            data = self._platform_admin_dashboard()
        elif role == CustomUser.Role.ORGANISATION_ADMIN:
            data = self._org_admin_dashboard(org)
        elif role == CustomUser.Role.PROGRAMME_MANAGER:
            data = self._programme_manager_dashboard(user, org)
        elif role == CustomUser.Role.MONITORING_OFFICER:
            data = self._monitoring_officer_dashboard(user, org)
        else:
            data = self._staff_dashboard(user, org)

        data["role"] = role
        data["role_display"] = user.get_role_display()
        return Response(data)

    def _platform_admin_dashboard(self):
        return {
            "total_organisations": Organisation.objects.count(),
            "total_users": User.objects.count(),
            "total_programmes": Programme.objects.count(),
            "total_participants": Participant.objects.count(),
            "total_surveys": Survey.objects.count(),
            "total_responses": SurveyResponse.objects.count(),
            "active_programmes": Programme.objects.filter(status=Programme.Status.ACTIVE).count(),
            "active_organisations": Organisation.objects.filter(is_active=True).count(),
        }

    def _org_admin_dashboard(self, org):
        if not org:
            return {}
        programmes = Programme.objects.filter(organisation=org)
        participants = Participant.objects.filter(organisation=org)
        surveys = Survey.objects.filter(organisation=org)
        responses = SurveyResponse.objects.filter(organisation=org)
        return {
            "organisation_id": str(org.id),
            "organisation_name": org.name,
            "total_programmes": programmes.count(),
            "active_programmes": programmes.filter(status=Programme.Status.ACTIVE).count(),
            "total_participants": participants.count(),
            "active_participants": participants.filter(status=Participant.Status.ACTIVE).count(),
            "total_surveys": surveys.count(),
            "published_surveys": surveys.filter(status=Survey.Status.PUBLISHED).count(),
            "total_responses": responses.count(),
        }

    def _programme_manager_dashboard(self, user, org):
        if not org:
            return {}
        programmes = Programme.objects.filter(organisation=org)
        participants = Participant.objects.filter(organisation=org)
        return {
            "organisation_id": str(org.id),
            "total_programmes": programmes.count(),
            "active_programmes": programmes.filter(status=Programme.Status.ACTIVE).count(),
            "total_participants": participants.count(),
            "recent_programmes": list(
                programmes.order_by("-created_at")[:5].values("id", "name", "status", "start_date")
            ),
        }

    def _monitoring_officer_dashboard(self, user, org):
        if not org:
            return {}
        surveys = Survey.objects.filter(organisation=org)
        responses = SurveyResponse.objects.filter(organisation=org)
        return {
            "organisation_id": str(org.id),
            "total_surveys": surveys.count(),
            "published_surveys": surveys.filter(status=Survey.Status.PUBLISHED).count(),
            "total_responses": responses.count(),
            "recent_responses": list(
                responses.order_by("-submitted_at")[:5].values(
                    "id", "survey__title", "respondent_name", "submitted_at"
                )
            ),
        }

    def _staff_dashboard(self, user, org):
        if not org:
            return {}
        surveys = Survey.objects.filter(created_by=user, organisation=org)
        responses = SurveyResponse.objects.filter(organisation=org)
        return {
            "organisation_id": str(org.id),
            "my_surveys": surveys.count(),
            "total_responses": responses.count(),
            "recent_surveys": list(
                surveys.order_by("-created_at")[:5].values("id", "title", "status", "created_at")
            ),
        }


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Org-scoped user management (platform admins / org admins)."""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return User.objects.all()
        return User.objects.filter(organisation=user.organisation)

    def perform_destroy(self, instance):
        audit(self.request.user, "user.delete", instance.email)
        instance.delete()


class UserListView(generics.ListCreateAPIView):
    """
    GET  /api/auth/users/ — list users (org-scoped; platform admin sees all).
    POST /api/auth/users/ — platform admin only (organisations cannot create
    their own users; the platform admin provisions every account).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        from .serializers import RegisterUserSerializer

        if self.request.method == "POST":
            return RegisterUserSerializer
        return UserSerializer

    def get_permissions(self):
        from apps.core.permissions import IsPlatformAdmin

        if self.request.method == "POST":
            return [IsPlatformAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return User.objects.all().select_related("organisation")
        return User.objects.filter(organisation=user.organisation).select_related(
            "organisation"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        audit(request.user, "user.create", f"created user {user.email}")
        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )