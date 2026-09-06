from django.urls import path

from .platform_admin_views import (
    PlatformOrganisationListView,
    PlatformUserListView,
    system_overview,
)

urlpatterns = [
    path("organisations/", PlatformOrganisationListView.as_view(), name="platform-orgs"),
    path("users/", PlatformUserListView.as_view(), name="platform-users"),
    path("system/", system_overview, name="platform-system"),
]