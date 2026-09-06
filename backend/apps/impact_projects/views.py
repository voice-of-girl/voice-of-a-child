from django.utils import timezone
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin
from apps.impact_projects.models import ImpactProject, ImpactResponse, ImpactSurvey
from apps.impact_projects.serializers import (
    ImpactProjectCreateSerializer,
    ImpactProjectSerializer,
    ImpactResponseSerializer,
    ImpactSubmitSerializer,
    ImpactSurveySerializer,
    ImpactSurveyWriteSerializer,
)


class ImpactProjectViewSet(viewsets.ModelViewSet):
    """Admin-driven standalone impact assessment projects."""

    queryset = ImpactProject.objects.prefetch_related("surveys").order_by("-created_at")
    permission_classes = [IsAdmin]
    search_fields = ["title", "client_organisation__name"]
    filterset_fields = ["status", "client_organisation"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ImpactProjectCreateSerializer
        return ImpactProjectSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get", "post"])
    def surveys(self, request, pk=None):
        project = self.get_object()
        if request.method == "GET":
            return Response(
                ImpactSurveySerializer(project.surveys.all(), many=True).data
            )
        write = ImpactSurveyWriteSerializer(data=request.data)
        write.is_valid(raise_exception=True)
        survey = write.save(project=project)
        return Response(ImpactSurveySerializer(survey).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get", "patch", "delete"],
        url_path=r"surveys/(?P<survey_id>[^/.]+)",
    )
    def survey_detail(self, request, pk=None, survey_id=None):
        project = self.get_object()
        survey = project.surveys.filter(id=survey_id).first()
        if not survey:
            return Response({"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.method == "DELETE":
            survey.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == "PATCH":
            write = ImpactSurveyWriteSerializer(survey, data=request.data, partial=True)
            write.is_valid(raise_exception=True)
            write.save()
        return Response(ImpactSurveySerializer(survey).data)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path=r"surveys/(?P<survey_id>[^/.]+)/responses",
    )
    def survey_responses(self, request, pk=None, survey_id=None):
        project = self.get_object()
        survey = project.surveys.filter(id=survey_id).first()
        if not survey:
            return Response({"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.method == "POST":
            # Creates an anonymous response with a fresh token to share.
            response = ImpactResponse.objects.create(survey=survey)
            return Response(ImpactResponseSerializer(response).data, status=status.HTTP_201_CREATED)
        return Response(ImpactResponseSerializer(survey.responses.all(), many=True).data)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"surveys/(?P<survey_id>[^/.]+)/links",
    )
    def survey_links(self, request, pk=None, survey_id=None):
        project = self.get_object()
        survey = project.surveys.filter(id=survey_id).first()
        if not survey:
            return Response({"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND)
        base = request.build_absolute_uri("/")[:-1]
        links = [
            {
                "response_id": r.id,
                "url": f"{base}/api/impact-projects/access/{r.access_token}/",
            }
            for r in survey.responses.filter(submitted=False)
        ]
        return Response(links)

    @action(
        detail=True,
        methods=["post"],
        url_path=r"surveys/(?P<survey_id>[^/.]+)/publish",
    )
    def publish_survey(self, request, pk=None, survey_id=None):
        project = self.get_object()
        survey = project.surveys.filter(id=survey_id).first()
        if not survey:
            return Response({"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND)
        survey.status = ImpactSurvey.Status.PUBLISHED
        survey.save()
        return Response(ImpactSurveySerializer(survey).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        project = self.get_object()
        project.status = ImpactProject.Status.COMPLETED
        project.save()
        return Response(ImpactProjectSerializer(project).data)


class ImpactPublicAccessView(views.APIView):
    """Public token-based access to an impact survey."""

    permission_classes = [AllowAny]

    def get_object(self, token):
        return (
            ImpactResponse.objects.select_related("survey")
            .filter(access_token=token)
            .first()
        )

    def get(self, request, token):
        response = self.get_object(token)
        if not response:
            return Response({"detail": "Invalid or expired link."}, status=status.HTTP_404_NOT_FOUND)
        if response.submitted:
            return Response({"detail": "Already submitted."}, status=status.HTTP_400_BAD_REQUEST)
        if response.survey.status != ImpactSurvey.Status.PUBLISHED:
            return Response({"detail": "Survey not open."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "survey": {
                    "id": response.survey.id,
                    "title": response.survey.title,
                    "description": response.survey.description,
                    "survey_type": response.survey.survey_type,
                    "questions": response.survey.questions,
                },
                "response_id": response.id,
            }
        )

    def post(self, request, token):
        response = self.get_object(token)
        if not response:
            return Response({"detail": "Invalid or expired link."}, status=status.HTTP_404_NOT_FOUND)
        if response.submitted:
            return Response({"detail": "Already submitted."}, status=status.HTTP_400_BAD_REQUEST)
        if response.survey.status != ImpactSurvey.Status.PUBLISHED:
            return Response({"detail": "Survey not open."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ImpactSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        required_ids = {q.get("id") for q in response.survey.questions if q.get("required")}
        answered_ids = {a.get("question_id") for a in data["answers"]}
        missing = required_ids - answered_ids
        if missing:
            return Response(
                {
                    "detail": "Missing answers for required questions.",
                    "question_ids": sorted(missing),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response.answers = data["answers"]
        response.respondent_name = data.get("respondent_name", "")
        response.respondent_phone = data.get("respondent_phone", "")
        response.submitted = True
        response.submitted_at = timezone.now()
        response.save()
        return Response({"detail": "Response recorded. Thank you!"}, status=status.HTTP_201_CREATED)