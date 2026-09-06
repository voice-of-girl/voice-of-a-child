"""Role-based and organisation-scoped permission classes."""
from rest_framework.permissions import SAFE_METHODS, BasePermission

PLATFORM_ADMIN = "PLATFORM_ADMIN"
ORGANISATION_ADMIN = "ORGANISATION_ADMIN"
PROGRAMME_MANAGER = "PROGRAMME_MANAGER"
MONITORING_OFFICER = "MONITORING_OFFICER"
STAFF = "STAFF"

# Roles that may write within their own organisation.
WRITE_ROLES = {ORGANISATION_ADMIN, PROGRAMME_MANAGER, MONITORING_OFFICER}

# Roles that may delete / administrate their organisation.
ADMIN_ROLES = {ORGANISATION_ADMIN}


class IsAuthenticatedOrgUser(BasePermission):
    """Authenticated user who belongs to an organisation (not platform admin)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.role != PLATFORM_ADMIN
            and user.organisation_id
        )


class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and user.role == PLATFORM_ADMIN
        )


class IsOrgAdminOrPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.role == PLATFORM_ADMIN:
            return True
        return user.role == ORGANISATION_ADMIN and user.organisation_id


class IsStaffOrAdmin(BasePermission):
    """Platform staff may *read* tenant data; platform admins may write."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.role == PLATFORM_ADMIN:
            return True
        if request.method in SAFE_METHODS and user.role in {ORGANISATION_ADMIN, PROGRAMME_MANAGER, MONITORING_OFFICER, STAFF}:
            return bool(user.organisation_id)
        return False


class CanWriteTenantData(BasePermission):
    """Authenticated org members that may create/update tenant data."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.role == PLATFORM_ADMIN:
            return True
        return user.role in WRITE_ROLES and bool(user.organisation_id)


class CanAdminTenantData(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.role == PLATFORM_ADMIN:
            return True
        return user.role in ADMIN_ROLES and bool(user.organisation_id)


def ensure_organisation_access(queryset, user):
    """
    Enforce tenant isolation at the queryset level.

    - Platform admins may access every organisation.
    - Any other user is restricted to their own organisation.
    Never trust an ``organisation_id`` supplied by the client.
    """
    if user.role == PLATFORM_ADMIN:
        return queryset
    return queryset.filter(organisation=user.organisation)