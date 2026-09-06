"""View mixins that guarantee organisation-scoped querysets."""
from rest_framework.exceptions import NotFound

from apps.core.permissions import PLATFORM_ADMIN, ensure_organisation_access


class TenantQuerysetMixin:
    """
    Scopes every queryset to the requesting user's organisation.

    Subclasses must define ``get_queryset`` OR set ``queryset``; this mixin
    chains the tenant restriction on top of the base queryset. Objects of
    another organisation simply do not resolve (404), preventing leakage.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if qs is None or user is None:
            return qs
        if not hasattr(qs.model, "organisation"):
            return qs
        return ensure_organisation_access(qs, user)

    def filter_queryset(self, queryset):
        """
        Enforce tenant isolation on every list endpoint.

        Subclasses may override ``get_queryset`` (for annotations, eager
        loading, filters), so the org restriction is additionally applied
        here — DRF runs ``filter_queryset`` for both list and detail.
        """
        qs = super().filter_queryset(queryset)
        user = self.request.user
        if qs is not None and user is not None and hasattr(qs.model, "organisation"):
            qs = ensure_organisation_access(qs, user)
        return qs

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        role = getattr(user, "role", None)
        if obj is not None and hasattr(obj, "organisation"):
            if role != PLATFORM_ADMIN and obj.organisation_id != user.organisation_id:
                raise NotFound("Object not found.")
        return obj


class ParentScopedMixin(TenantQuerysetMixin):
    """
    Resolves a ``<parent>_id`` URL kwarg and makes the parent available as
    ``self.parent_obj`` while enforcing that it belongs to the caller's
    organisation. Use for nested resources such as programme participants.
    """

    parent_lookup_kwarg = "programme_id"
    parent_queryset = None  # set by the subclass

    def get_parent_obj(self):
        parent_id = self.kwargs.get(self.parent_lookup_kwarg)
        if parent_id is None:
            return None
        qs = self.parent_queryset
        user = self.request.user
        qs = ensure_organisation_access(qs, user)
        try:
            return qs.get(id=parent_id)
        except qs.model.DoesNotExist:
            raise NotFound("Parent object not found.")

    def initial(self, request, *args, **kwargs):
        self.parent_obj = self.get_parent_obj()
        super().initial(request, *args, **kwargs)