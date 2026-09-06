"""Authenticated survey management views."""
from django.db.models import Count
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import CanAdminTenantData, CanWriteTenantData
from apps.core.services import audit

from .models import Survey, SurveyResponse
from .serializers import (
    SurveyResponseSerializer,
    SurveySerializer,
)


class SurveyViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title", "status"]

    def get_permissions(self):
        if self.action == "destroy":
            return [CanAdminTenantData()]
        return [CanWriteTenantData()]

    def get_queryset(self):
        qs = (
            Survey.objects.select_related("organisation", "programme", "impact_project")
            .prefetch_related("questions")
            .annotate(responses_count=Count("responses"))
        )
        programme = self.request.query_params.get("programme")
        project = self.request.query_params.get("impact_project")
        status_filter = self.request.query_params.get("status")
        if programme:
            qs = qs.filter(programme_id=programme)
        if project:
            qs = qs.filter(impact_project_id=project)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        survey = serializer.save(
            organisation=self.request.user.organisation,
            created_by=self.request.user,
        )
        audit(self.request.user, "survey.create", survey.title)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        audit(self.request.user, "survey.delete", instance.title)
        instance.delete()

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        survey = self.get_object()
        if not survey.questions.exists():
            return Response(
                {"detail": "Add at least one question before publishing."}, status=400
            )
        survey.status = Survey.Status.PUBLISHED
        survey.save(update_fields=["status"])
        audit(request.user, "survey.publish", survey.title)
        return Response(self.get_serializer(survey).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        survey = self.get_object()
        survey.status = Survey.Status.CLOSED
        survey.save(update_fields=["status"])
        audit(request.user, "survey.close", survey.title)
        return Response(self.get_serializer(survey).data)

    @action(detail=True, methods=["get"])
    def responses(self, request, pk=None):
        survey = self.get_object()
        qs = (
            survey.responses.select_related("participant", "programme")
            .prefetch_related("answers__question")
        )
        page = self.paginate_queryset(qs)
        serializer = SurveyResponseSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Response stats for a single survey (charts-friendly)."""
        survey = self.get_object()
        responses = survey.responses.all()
        total = responses.count()
        return Response(
            {
                "survey_id": str(survey.id),
                "title": survey.title,
                "status": survey.status,
                "responses_total": total,
                "responses_per_day": list(
                    responses.extra({"day": "date(submitted_at)"})
                    .values("day")
                    .annotate(count=Count("id"))
                    .order_by("day")
                ),
            }
        )


class SurveyResponseViewSet(TenantQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only listing/detail of survey responses (org-scoped)."""

    serializer_class = SurveyResponseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["respondent_name", "respondent_email", "participant__name"]
    ordering_fields = ["submitted_at"]

    def get_queryset(self):
        qs = (
            SurveyResponse.objects.select_related("organisation", "survey", "programme", "participant")
            .prefetch_related("answers__question")
        )
        survey = self.request.query_params.get("survey")
        programme = self.request.query_params.get("programme")
        if survey:
            qs = qs.filter(survey_id=survey)
        if programme:
            qs = qs.filter(programme_id=programme)
        return qs