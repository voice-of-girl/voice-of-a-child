"""Role-based and organisation-scoped permissions.

Data isolation is enforced at the backend: an ORGANISATION user may only
ever see records belonging to their own organisation. ADMIN users have
unrestricted access.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.accounts.models import CustomUser


def user_is_admin(user):
    return bool(
        user and user.is_authenticated and user.role == CustomUser.Role.ADMIN
    )


def user_is_organisation(user):
    return bool(
        user
        and user.is_authenticated
        and user.role == CustomUser.Role.ORGANISATION
        and user.organisation_id is not None
    )


class IsAdmin(BasePermission):
    """Allows access only to platform administrators."""

    def has_permission(self, request, view):
        return user_is_admin(request.user)


class IsOrganisationUser(BasePermission):
    """Allows access only to organisation users with an organisation."""

    def has_permission(self, request, view):
        return user_is_organisation(request.user)


class IsAdminOrOrganisationUser(IsAuthenticated):
    """Allows any authenticated user (both roles)."""

    def has_permission(self, request, view):
        authenticated = super().has_permission(request, view)
        return authenticated and (
            user_is_admin(request.user) or user_is_organisation(request.user)
        )


class IsAdminOrOrganisationOwner(BasePermission):
    """Object-level check: organisation users may only touch their own org's objects.

    Works for any object exposing ``organisation_id`` (directly or through
    ``get_organisation_id()``).
    """

    def has_object_permission(self, request, view, obj):
        if user_is_admin(request.user):
            return True
        if not user_is_organisation(request.user):
            return False
        org_id = getattr(obj, "organisation_id", None)
        if org_id is None:
            org_id = getattr(obj, "get_organisation_id", lambda: None)()
        return org_id == request.user.organisation_id


def scope_queryset(queryset, user, organisation_field="organisation"):
    """Return admin-unrestricted or org-scoped queryset."""
    if user_is_admin(user):
        return queryset
    if user_is_organisation(user):
        return queryset.filter(**{f"{organisation_field}_id": user.organisation_id})
    return queryset.none()