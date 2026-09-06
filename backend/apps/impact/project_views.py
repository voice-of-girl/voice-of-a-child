"""Standalone impact project views."""
from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import CanAdminTenantData, CanWriteTenantData
from apps.core.services import audit
from apps.surveys.models import Survey
from apps.surveys.serializers import SurveySerializer

from .models import ImpactProject, KPI
from .serializers import ImpactProjectSerializer


class ImpactProjectViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ImpactProjectSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [CanAdminTenantData()]
        return [CanWriteTenantData()]

    def get_queryset(self):
        return (
            ImpactProject.objects.select_related("organisation")
            .annotate(
                surveys_count=Count("surveys", distinct=True),
                responses_count=Count("survey_responses", distinct=True),
            )
        )

    def perform_create(self, serializer):
        project = serializer.save(
            organisation=self.request.user.organisation,
            created_by=self.request.user,
        )
        audit(self.request.user, "impact_project.create", project.name)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        audit(self.request.user, "impact_project.delete", instance.name)
        instance.delete()

    @action(detail=True, methods=["get", "post"])
    def surveys(self, request, pk=None):
        """List surveys for this project, or create a new one."""
        project = self.get_object()
        if request.method == "GET":
            qs = project.surveys.select_related("organisation", "programme", "impact_project")
            page = self.paginate_queryset(qs)
            serializer = SurveySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SurveySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        survey = serializer.save(
            organisation=request.user.organisation,
            impact_project=project,
            created_by=request.user,
        )
        return Response(SurveySerializer(survey).data, status=201)

    @action(detail=True, methods=["get"])
    def analysis(self, request, pk=None):
        """Project-level analysis: responses, rate, KPIs and progress."""
        project = self.get_object()
        surveys = project.surveys.all()
        responses = project.survey_responses.all()
        total_responses = responses.count()

        surveys_data = []
        for survey in surveys:
            count = survey.responses.count()
            surveys_data.append(
                {
                    "survey_id": str(survey.id),
                    "survey": survey.title,
                    "stage": survey.stage,
                    "status": survey.status,
                    "responses": count,
                }
            )
        kpis = KPI.objects.filter(organisation=request.user.organisation, impact_project=project)
        kpi_data = [
            {
                "id": str(k.id),
                "kpi": k.name,
                "unit": k.unit,
                "baseline": k.baseline,
                "current": k.current_value,
                "target": k.target,
                "progress_percentage": k.progress_percentage,
            }
            for k in kpis
        ]
        return Response(
            {
                "project": ImpactProjectSerializer(project).data,
                "surveys": surveys_data,
                "total_responses": total_responses,
                "surveys_count": surveys.count(),
                "kpis": kpi_data,
            }
        )