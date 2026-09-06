"""Report views: list, generate and download (org-scoped)."""
from django.http import FileResponse, Http404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantQuerysetMixin
from apps.core.permissions import CanAdminTenantData, CanWriteTenantData
from apps.core.services import audit

from .models import Report
from .serializers import ReportGenerateSerializer, ReportSerializer
from .services import generate_report


class ReportViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["title"]
    ordering_fields = ["created_at", "title"]

    def get_permissions(self):
        if self.action == "destroy":
            return [CanAdminTenantData()]
        return [CanWriteTenantData()]

    def get_queryset(self):
        qs = (
            Report.objects.select_related(
                "organisation", "programme", "survey", "impact_project"
            )
        )
        report_type = self.request.query_params.get("report_type")
        file_format = self.request.query_params.get("file_format")
        programme = self.request.query_params.get("programme")
        if report_type:
            qs = qs.filter(report_type=report_type)
        if file_format:
            qs = qs.filter(file_format=file_format)
        if programme:
            qs = qs.filter(programme_id=programme)
        return qs

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """Create and generate a report synchronously."""
        org = request.user.organisation
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        programme = survey = project = None
        # Tenant scoping: parents must live inside an organisation this user
        # may act upon (platform admins may target any organisation).
        visible_org_ids = request.user.organisations_visible().values_list(
            "id", flat=True
        )
        if data.get("programme"):
            from apps.programmes.models import Programme

            programme = Programme.objects.filter(
                id=data["programme"], organisation_id__in=visible_org_ids
            ).first()
            if programme is None:
                return Response({"detail": "Programme not found."}, status=404)
        if data.get("survey"):
            from apps.surveys.models import Survey

            survey = Survey.objects.filter(
                id=data["survey"], organisation_id__in=visible_org_ids
            ).first()
            if survey is None:
                return Response({"detail": "Survey not found."}, status=404)
        if data.get("impact_project"):
            from apps.impact.models import ImpactProject

            project = ImpactProject.objects.filter(
                id=data["impact_project"], organisation_id__in=visible_org_ids
            ).first()
            if project is None:
                return Response({"detail": "Impact project not found."}, status=404)

        report = Report.objects.create(
            organisation=org,
            programme=programme,
            survey=survey,
            impact_project=project,
            report_type=data["report_type"],
            title=data["title"] or "",
            file_format=data["file_format"],
            parameters=data,
            created_by=request.user,
        )
        generate_report(report)
        audit(request.user, "report.generate", f"{report.title} ({report.file_format})")
        return Response(
            ReportSerializer(report, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download the generated file (org-isolated via get_object)."""
        report = self.get_object()
        if not report.file or report.status != Report.Status.READY:
            raise Http404("Report is not ready.")
        # FileResponse streams from storage; filename drives Content-Type and
        # the attachment Content-Disposition without trusting client input.
        return FileResponse(
            report.file.open("rb"), as_attachment=True, filename=report.filename
        )