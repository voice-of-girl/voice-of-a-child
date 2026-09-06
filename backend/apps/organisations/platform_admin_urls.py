from django.urls import path
from rest_framework.routers import DefaultRouter

from .platform_admin_views import (
    PlatformOrgAdminAccountView,
    PlatformOrganisationDetailView,
    PlatformOrganisationListCreateView,
    PlatformUserListView,
    system_overview,
)
from .views import OrganisationViewSet

router = DefaultRouter(trailing_slash=True)
router.register("all-organisations", OrganisationViewSet, basename="platform-all-orgs")

urlpatterns = [
    path(
        "organisations/",
        PlatformOrganisationListCreateView.as_view(),
        name="platform-orgs",
    ),
    path(
        "organisations/<uuid:pk>/",
        PlatformOrganisationDetailView.as_view(),
        name="platform-org-detail",
    ),
    path(
        "organisations/<uuid:pk>/create-admin/",
        PlatformOrgAdminAccountView.as_view(),
        name="platform-org-create-admin",
    ),
    path("users/", PlatformUserListView.as_view(), name="platform-users"),
    path("system/", system_overview, name="platform-system"),
] + router.urls