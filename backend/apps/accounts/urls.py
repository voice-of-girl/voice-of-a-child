from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import AuthViewSet, BootstrapSuperuserView, LoginView, PasswordResetView, UserViewSet

router = DefaultRouter()
router.register("login", LoginView, basename="auth-login")
router.register("", AuthViewSet, basename="auth")
router.register("users", UserViewSet, basename="users")
router.register("password-reset", PasswordResetView, basename="password-reset")

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("bootstrap-superuser/", BootstrapSuperuserView.as_view({"post": "create"}), name="bootstrap-superuser"),
    path("", include(router.urls)),
]