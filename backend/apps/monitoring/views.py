"""Monitoring views (challenges, feedback, support requests)."""
from datetime import timedelta

from django.db.models import Avg, Count, F, Q
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import CanAdminTenantData, CanWriteTenantData
from apps.core.services import audit
from apps.programmes.models import Programme

from .models import Challenge, Feedback, SupportRequest
from .serializers import (
    ChallengeSerializer,
    FeedbackSerializer,
    SupportRequestSerializer,
)


class _MonitoringViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["created_at", "status", "category"]

    def get_permissions(self):
        if self.action == "destroy":
            return [CanAdminTenantData()]
        return [CanWriteTenantData()]

    def _filter_query(self, qs):
        programme = self.request.query_params.get("programme")
        status_filter = self.request.query_params.get("status")
        if programme:
            qs = qs.filter(programme_id=programme)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save(organisation=self.request.user.organisation)
        audit(self.request.user, f"{self.basename}.create", str(obj.id))


class ChallengeViewSet(_MonitoringViewSet):
    serializer_class = ChallengeSerializer
    search_fields = ["title", "description", "participant__name"]

    def get_queryset(self):
        qs = Challenge.objects.select_related("organisation", "programme", "participant", "assigned_to")
        return self._filter_query(qs)

    def perform_create(self, serializer):
        super().perform_create(serializer)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Aggregated monitoring statistics for dashboard cards & charts."""
        qs = self.get_queryset()
        total = qs.count()
        by_status = dict(qs.values_list("status").annotate(c=Count("id")))
        by_category = list(qs.values("category").annotate(count=Count("id")).order_by("-count"))

        # Resolution rate
        resolved = by_status.get(Challenge.Status.RESOLVED, 0)
        resolution_rate = round(resolved / total * 100, 1) if total else 0.0

        # Average resolution time (hours)
        resolved_qs = Challenge.objects.filter(
            organisation=self.request.user.organisation, resolved_at__isnull=False
        )
        avg_seconds = resolved_qs.aggregate(avg=Avg(F("resolved_at") - F("created_at")))["avg"]
        avg_hours = round(avg_seconds.total_seconds() / 3600) if avg_seconds else 0

        # Challenges over time (per week going back ~12 weeks)
        since = timezone.now() - timedelta(weeks=12)
        over_time = list(
            qs.filter(created_at__gte=since)
            .extra(select={"week": "strftime('%Y-W%W', created_at)"})
            .values("week")
            .annotate(count=Count("id"))
            .order_by("week")
        )

        return Response(
            {
                "total_challenges": total,
                "open": by_status.get(Challenge.Status.OPEN, 0),
                "in_progress": by_status.get(Challenge.Status.IN_PROGRESS, 0),
                "resolved": resolved,
                "resolution_rate": resolution_rate,
                "average_resolution_hours": avg_hours,
                "by_category": by_category,
                "over_time": over_time,
            }
        )


class FeedbackViewSet(_MonitoringViewSet):
    serializer_class = FeedbackSerializer
    search_fields = ["message", "participant__name"]

    def get_queryset(self):
        qs = Feedback.objects.select_related("organisation", "programme", "participant")
        return self._filter_query(qs)


class SupportRequestViewSet(_MonitoringViewSet):
    serializer_class = SupportRequestSerializer
    search_fields = ["description", "participant__name"]

    def get_queryset(self):
        qs = SupportRequest.objects.select_related("organisation", "programme", "participant", "assigned_to")
        return self._filter_query(qs)