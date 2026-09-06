from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminOrOrganisationUser
from apps.programmes.models import (
    Programme,
    ProgrammeEnrollment,
    ProgrammeKPI,
)
from apps.programmes.serializers import (
    ProgrammeEnrollmentCreateSerializer,
    ProgrammeEnrollmentSerializer,
    ProgrammeKPISerializer,
    ProgrammeSerializer,
    ProgrammeWriteSerializer,
)


class ProgrammeViewSet(viewsets.ModelViewSet):
    """CRUD for programmes. Organisations only see/manage their own."""

    queryset = Programme.objects.select_related("organisation").order_by("-created_at")
    permission_classes = [IsAdminOrOrganisationUser]
    search_fields = ["title", "description", "category", "location"]
    filterset_fields = ["status", "category", "organisation"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ProgrammeWriteSerializer
        return ProgrammeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organisation_id"] = (
            self.request.user.organisation_id
            if getattr(self.request.user, "role", None) == "ORGANISATION"
            else self.request.data.get("organisation_id")
        )
        context["created_by"] = self.request.user if self.request.user.is_authenticated else None
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.annotate(
                participants_count=Count("enrollments", distinct=True),
                active_count=Count(
                    "enrollments",
                    filter=Q(enrollments__status=ProgrammeEnrollment.Status.ACTIVE),
                    distinct=True,
                ),
                completed_count=Count(
                    "enrollments",
                    filter=Q(enrollments__status=ProgrammeEnrollment.Status.COMPLETED),
                    distinct=True,
                ),
                dropped_out_count=Count(
                    "enrollments",
                    filter=Q(enrollments__status=ProgrammeEnrollment.Status.DROPPED_OUT),
                    distinct=True,
                ),
            )
        if getattr(self.request.user, "role", None) == "ADMIN":
            return qs
        return qs.filter(organisation_id=self.request.user.organisation_id)

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) == "ORGANISATION":
            organisation_id = self.request.user.organisation_id
        else:
            organisation_id = serializer.context["organisation_id"]
        serializer.save(organisation_id=organisation_id)

    @action(detail=True, methods=["get"])
    def participants(self, request, pk=None):
        programme = self.get_object()
        self.check_object_permissions(request, programme)
        enrollments = programme.enrollments.select_related("participant").all()
        return Response(ProgrammeEnrollmentSerializer(enrollments, many=True).data)

    @action(detail=True, methods=["post"])
    def enroll(self, request, pk=None):
        programme = self.get_object()
        self.check_object_permissions(request, programme)
        serializer = ProgrammeEnrollmentCreateSerializer(
            data=request.data, context={"programme": programme}
        )
        serializer.is_valid(raise_exception=True)
        enrollment, created = ProgrammeEnrollment.objects.get_or_create(
            programme=programme,
            participant=serializer.validated_data["participant"],
            defaults={
                "status": serializer.validated_data.get("status", ProgrammeEnrollment.Status.ENROLLED)
            },
        )
        if not created:
            return Response(
                {"detail": "Participant is already enrolled in this programme."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            ProgrammeEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path=r"participants/(?P<participant_id>[^/.]+)/status",
    )
    def participant_status(self, request, pk=None, participant_id=None):
        programme = self.get_object()
        self.check_object_permissions(request, programme)
        new_status = request.data.get("status")
        if new_status not in ProgrammeEnrollment.Status.values:
            return Response(
                {"detail": f"status must be one of {ProgrammeEnrollment.Status.values}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        enrollment = programme.enrollments.filter(participant_id=participant_id).first()
        if not enrollment:
            return Response(
                {"detail": "Participant is not enrolled in this programme."},
                status=status.HTTP_404_NOT_FOUND,
            )
        enrollment.status = new_status
        if new_status in (ProgrammeEnrollment.Status.COMPLETED, ProgrammeEnrollment.Status.DROPPED_OUT):
            from django.utils import timezone

            enrollment.completed_at = timezone.now()
        else:
            enrollment.completed_at = None
        enrollment.save()
        return Response(ProgrammeEnrollmentSerializer(enrollment).data)

    @action(detail=True, methods=["get"])
    def kpis(self, request, pk=None):
        programme = self.get_object()
        self.check_object_permissions(request, programme)
        return Response(ProgrammeKPISerializer(programme.kpis.all(), many=True).data)

    @action(detail=True, methods=["post"])
    def add_kpi(self, request, pk=None):
        programme = self.get_object()
        self.check_object_permissions(request, programme)
        serializer = ProgrammeKPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kpi = serializer.save(programme=programme)
        return Response(ProgrammeKPISerializer(kpi).data, status=status.HTTP_201_CREATED)
class ProgrammeKPIViewSet(viewsets.ModelViewSet):
    """Update a single KPI's current/baseline values, etc."""

    queryset = ProgrammeKPI.objects.select_related("programme").all()
    serializer_class = ProgrammeKPISerializer
    permission_classes = [IsAdminOrOrganisationUser]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "ADMIN":
            return qs
        return qs.filter(programme__organisation_id=self.request.user.organisation_id)


class ProgrammeEnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """List/retrieve enrollments (org-scoped)."""

    queryset = ProgrammeEnrollment.objects.select_related("programme", "participant").all()
    serializer_class = ProgrammeEnrollmentSerializer
    permission_classes = [IsAdminOrOrganisationUser]
    filterset_fields = ["programme", "participant", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "ADMIN":
            return qs
        return qs.filter(programme__organisation_id=self.request.user.organisation_id)