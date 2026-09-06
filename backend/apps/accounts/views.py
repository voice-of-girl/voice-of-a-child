from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.permissions import IsAdmin, IsAdminOrOrganisationUser, user_is_admin
from apps.accounts.serializers import (
    LoginSerializer,
    OrganisationalUserCreateSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)

User = get_user_model()


def _get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginView(viewsets.ViewSet):
    """Authenticate and return JWT access + refresh tokens, user info and role."""

    permission_classes = [AllowAny]

    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data["email"].lower())
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.check_password(serializer.validated_data["password"]):
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(
            {
                **_get_tokens_for_user(user),
                "user": UserSerializer(user).data,
            }
        )


class AuthViewSet(viewsets.ViewSet):
    """Authenticated helpers: /me and /logout."""

    permission_classes = [IsAdminOrOrganisationUser]

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        try:
            refresh = request.data.get("refresh")
            if refresh:
                token = RefreshToken(refresh)
                token.blacklist()
        except Exception:
            pass
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
class UserViewSet(viewsets.ModelViewSet):
    """Admin manages organisation users. Org users may update their own profile."""

    queryset = User.objects.select_related("organisation").order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "patch", "delete", "post", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrganisationalUserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = OrganisationalUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get("new_password")
        if not new_password or len(new_password) < 8:
            return Response(
                {"detail": "new_password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password reset successfully."})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(UserSerializer(user).data)


class PasswordResetView(viewsets.ViewSet):
    """Password reset for authenticated org users (self-service)."""

    permission_classes = [IsAdminOrOrganisationUser]

    def create(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        if email != request.user.email and not user_is_admin(request.user):
            return Response(
                {"detail": "You can only reset your own password."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"detail": "Confirmation accepted; provide new_password."})

    @action(detail=False, methods=["post"])
    def confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        if email != request.user.email and not user_is_admin(request.user):
            return Response(
                {"detail": "You can only reset your own password."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."})


class RefreshView(TokenRefreshView):
    """Overrides config.urls reference for clarity (SimpleJWT defaults retained)."""


class BootstrapSuperuserView(viewsets.ViewSet):
    """One-time endpoint to create the first superuser when no shell is available."""

    permission_classes = [AllowAny]

    def create(self, request):
        if User.objects.filter(is_superuser=True).exists():
            return Response(
                {"detail": "A superuser already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = request.data.get("email", "").lower()
        password = request.data.get("password", "")
        first_name = request.data.get("first_name", "")
        last_name = request.data.get("last_name", "")
        if not email or not password or not first_name or not last_name:
            return Response(
                {"detail": "email, password, first_name and last_name are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        return Response(
            {"detail": "Superuser created.", "email": user.email},
            status=status.HTTP_201_CREATED,
        )