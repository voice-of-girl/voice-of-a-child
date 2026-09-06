from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import (
    IsAdmin,
    IsAdminOrOrganisationUser,
    scope_queryset,
)
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.participants.serializers import (
    ParticipantClaimSerializer,
    ParticipantSerializer,
    ParticipantVerifySerializer,
    ParticipantWriteSerializer,
)


class ParticipantRegisterView(CreateAPIView):
    """Public registration — participants do NOT receive login credentials."""

    serializer_class = ParticipantWriteSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        context = {"organisation_id": None}
        serializer = ParticipantWriteSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        participant = serializer.save(organisation=None)
        return Response(
            ParticipantSerializer(participant).data, status=status.HTTP_201_CREATED
        )


class ParticipantViewSet(viewsets.ModelViewSet):
    """Organisation-scoped participant management with search/filter/verify/claim."""

    queryset = Participant.objects.select_related("organisation").order_by("-created_at")
    permission_classes = [IsAdminOrOrganisationUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["full_name", "phone_number", "email", "district", "skills"]
    ordering_fields = ["created_at", "full_name", "district"]
    filterset_fields = [
        "district",
        "education_level",
        "employment_status",
        "verification_status",
        "gender",
        "organisation",
    ]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ParticipantWriteSerializer
        return ParticipantSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organisation_id"] = (
            self.request.user.organisation_id
            if getattr(self.request.user, "role", None) == "ORGANISATION"
            else self.request.query_params.get("organisation_id")
        )
        return context

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.role == "ADMIN":
            return qs
        # Organisation users see their own participants plus unclaimed registry records.
        own = qs.filter(organisation_id=user.organisation_id)
        orphaned = qs.filter(organisation_id__isnull=True)
        # Ensure the same instance never appears twice after combine.
        ids = set(own.values_list("id", flat=True)) | set(orphaned.values_list("id", flat=True))
        return Participant.objects.filter(id__in=ids).select_related("organisation")

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) == "ORGANISATION":
            serializer.save(organisation_id=self.request.user.organisation_id)
        else:
            organisation_id = self.request.data.get("organisation_id")
            if not organisation_id:
                serializer.save(organisation=None)
            else:
                serializer.save(organisation_id=organisation_id)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        participant = self.get_object()
        serializer = ParticipantVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant.verification_status = serializer.validated_data["verification_status"]
        participant.save()
        return Response(ParticipantSerializer(participant).data)

    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        """Organisation claims a publicly-registered (unclaimed) participant."""
        participant = self.get_object()
        serializer = ParticipantClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if participant.organisation_id is not None:
            return Response(
                {"detail": "This participant already belongs to an organisation."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Organisation.objects.filter(id=serializer.validated_data["organisation_id"]).exists():
            return Response(
                {"detail": "Organisation does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user.role == "ORGANISATION" and (
            serializer.validated_data["organisation_id"] != request.user.organisation_id
        ):
            return Response(
                {"detail": "You can only claim participants for your own organisation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        participant.organisation_id = serializer.validated_data["organisation_id"]
        participant.save()
        return Response(ParticipantSerializer(participant).data)