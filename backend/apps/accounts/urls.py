from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    PasswordChangeView,
    RefreshView,
    RegisterUserView,
    UserDetailView,
    UserListView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("register/", RegisterUserView.as_view(), name="auth-register"),
    path("password/change/", PasswordChangeView.as_view(), name="auth-password-change"),
    path("users/", UserListView.as_view(), name="auth-users"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="auth-user-detail"),
]