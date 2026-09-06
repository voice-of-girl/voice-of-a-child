from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminOrOrganisationUser
from apps.participants.models import Participant
from apps.programmes.models import Programme
from apps.surveys.models import (
    Answer,
    Question,
    Survey,
    SurveyAssignment,
    SurveyResponse,
)
from apps.surveys.serializers import (
    PublicSurveySerializer,
    PublicSurveySubmitSerializer,
    QuestionWriteSerializer,
    SurveyAssignSerializer,
    SurveyResponseSerializer,
    SurveySerializer,
    SurveyWriteSerializer,
)


class SurveyViewSet(viewsets.ModelViewSet):
    """Survey CRUD, publishing, assignment and response management."""

    queryset = Survey.objects.select_related("organisation", "programme").order_by("-created_at")
    permission_classes = [IsAdminOrOrganisationUser]
    search_fields = ["title", "description"]
    filterset_fields = ["status", "survey_type", "programme", "organisation"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return SurveyWriteSerializer
        return SurveySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.annotate(
                response_count=Count("responses", distinct=True),
                submitted_count=Count(
                    "responses", filter=Q(responses__submitted=True), distinct=True
                ),
            )
        if getattr(self.request.user, "role", None) == "ADMIN":
            return qs
        return qs.filter(organisation_id=self.request.user.organisation_id)

    def get_object_organisation(self, obj):
        return obj.organisation_id

    def perform_create(self, serializer):
        organisation_id = (
            self.request.user.organisation_id
            if getattr(self.request.user, "role", None) == "ORGANISATION"
            else self.request.data.get("organisation_id")
        )
        serializer.save(
            organisation_id=organisation_id,
            created_by=self.request.user if self.request.user.is_authenticated else None,
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        survey.status = Survey.Status.PUBLISHED
        survey.save()
        return Response(SurveySerializer(survey).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        survey.status = Survey.Status.UNPUBLISHED
        survey.save()
        return Response(SurveySerializer(survey).data)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign survey to specific participants and/or an entire programme."""
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        serializer = SurveyAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        targets = []
        if data.get("programme_id"):
            programme = Programme.objects.filter(
                id=data["programme_id"], organisation_id=survey.organisation_id
            ).first()
            if not programme:
                return Response(
                    {"detail": "Programme not found in this organisation."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if data.get("participant_ids"):
                participant_qs = programme.enrollments.filter(
                    participant_id__in=data["participant_ids"]
                )
                targets = list(participant_qs.values_list("participant_id", flat=True))
            else:
                targets = list(programme.enrollments.values_list("participant_id", flat=True))
            # Programme-level assignment marker
            SurveyAssignment.objects.get_or_create(survey=survey, programme=programme)
        elif data.get("participant_ids"):
            participant_qs = Participant.objects.filter(
                id__in=data["participant_ids"], organisation_id=survey.organisation_id
            )
            targets = list(participant_qs.values_list("id", flat=True))

        created, skipped = 0, 0
        for pid in targets:
            _, was_created = SurveyAssignment.objects.get_or_create(survey=survey, participant_id=pid)
            response, _ = SurveyResponse.objects.get_or_create(
                survey=survey,
                participant_id=pid,
                organisation_id=survey.organisation_id,
            )
            if was_created:
                created += 1
        return Response(
            {
                "detail": "Survey assigned.",
                "assigned": created,
                "existing": skipped,
                "total_targets": len(targets),
            }
        )

    @action(detail=True, methods=["get"])
    def questions(self, request, pk=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        return Response(QuestionWriteSerializer(survey.questions.all(), many=True).data)

    @action(detail=True, methods=["post"])
    def add_question(self, request, pk=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        serializer = QuestionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = request.data.get("order") or survey.questions.count()
        question = serializer.save(survey=survey, order=order)
        return Response(QuestionWriteSerializer(question).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch", "delete"],
        url_path=r"questions/(?P<question_id>[^/.]+)",
    )
    def update_delete_question(self, request, pk=None, question_id=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        question = survey.questions.filter(id=question_id).first()
        if not question:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.method == "DELETE":
            question.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = QuestionWriteSerializer(question, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(QuestionWriteSerializer(question).data)

    @action(detail=True, methods=["get"])
    def responses(self, request, pk=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        responses = survey.responses.prefetch_related("answers__question").order_by("-created_at")
        submitted = request.query_params.get("submitted")
        if submitted is not None:
            responses = responses.filter(submitted=submitted.lower() == "true")
        return Response(SurveyResponseSerializer(responses, many=True).data)

    @action(detail=True, methods=["get"])
    def links(self, request, pk=None):
        """Return the secure public links for issued responses."""
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        responses = survey.responses.all()
        base = request.build_absolute_uri("/")[:-1]
        links = [
            {
                "response_id": r.id,
                "participant_id": r.participant_id,
                "participant_name": r.participant.full_name if r.participant else None,
                "url": f"{base}/api/surveys/link/{r.access_token}/",
            }
            for r in responses
        ]
        return Response(links)

    @action(detail=True, methods=["get"])
    def completion_rate(self, request, pk=None):
        survey = self.get_object()
        self.check_object_permissions(request, survey)
        assigned = survey.assignments.exclude(participant__isnull=True).count()
        submitted = survey.responses.filter(submitted=True).count()
        rate = round((submitted / assigned) * 100, 1) if assigned else 0.0
        return Response(
            {
                "survey": survey.id,
                "assigned": assigned,
                "submitted": submitted,
                "completion_rate": rate,
            }
        )