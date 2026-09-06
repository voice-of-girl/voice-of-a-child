from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.organisations.views import MyOrganisationViewSet, OrganisationViewSet

router = DefaultRouter()
router.register("", OrganisationViewSet, basename="organisations")

urlpatterns = [
    path("my/", MyOrganisationViewSet.as_view({"get": "list"}), name="my-organisation"),
    path("", include(router.urls)),
]
