"""Report serializers."""
from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.name", read_only=True)
    scope_name = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    filename = serializers.CharField(read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "organisation",
            "organisation_name",
            "programme",
            "survey",
            "impact_project",
            "report_type",
            "title",
            "status",
            "file_format",
            "parameters",
            "file",
            "scope_name",
            "download_url",
            "filename",
            "error_message",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "organisation",
            "status",
            "file",
            "created_at",
        ]

    def get_scope_name(self, obj):
        if obj.programme_id:
            return obj.programme.name
        if obj.survey_id:
            return obj.survey.title
        if obj.impact_project_id:
            return obj.impact_project.name
        return obj.organisation.name

    def get_download_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            url = f"/api/reports/{obj.id}/download/"
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class ReportGenerateSerializer(serializers.Serializer):
    """Parameters for generating a new report."""

    report_type = serializers.ChoiceField(choices=Report.ReportType.choices)
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    file_format = serializers.ChoiceField(
        choices=Report.FileFormat.choices, default=Report.FileFormat.PDF
    )
    programme = serializers.UUIDField(required=False, allow_null=True)
    survey = serializers.UUIDField(required=False, allow_null=True)
    impact_project = serializers.UUIDField(required=False, allow_null=True)