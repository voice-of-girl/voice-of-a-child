"""Impact serializers."""
from rest_framework import serializers

from .models import ImpactMeasurement, ImpactProject, KPI


class KPISerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source="programme.name", read_only=True, default=None)
    project_name = serializers.CharField(source="impact_project.name", read_only=True, default=None)
    progress_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = KPI
        fields = [
            "id",
            "organisation",
            "programme",
            "programme_name",
            "impact_project",
            "project_name",
            "name",
            "description",
            "unit",
            "baseline",
            "current_value",
            "target",
            "endline",
            "status",
            "trend_data",
            "progress_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class ImpactProjectSerializer(serializers.ModelSerializer):
    surveys_count = serializers.IntegerField(read_only=True, default=0)
    responses_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = ImpactProject
        fields = [
            "id",
            "organisation",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "surveys_count",
            "responses_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class ImpactMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactMeasurement
        fields = ["id", "organisation", "programme", "survey", "kpi", "impact_project", "metric", "value", "period", "notes", "created_at"]
        read_only_fields = ["id", "organisation", "created_at"]