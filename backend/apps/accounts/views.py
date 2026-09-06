"""Authentication and account views."""
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.permissions import IsPlatformAdmin
from apps.core.services import audit

from .serializers import (
    MeSerializer,
    PasswordChangeSerializer,
    RegisterUserSerializer,
    UserSerializer,
)

User = get_user_model()


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ with {email, password}."""

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