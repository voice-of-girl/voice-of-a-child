from rest_framework import serializers

from apps.impact_projects.models import ImpactProject, ImpactResponse, ImpactSurvey


class ImpactSurveySerializer(serializers.ModelSerializer):
    response_count = serializers.SerializerMethodField()
    submitted_count = serializers.SerializerMethodField()

    class Meta:
        model = ImpactSurvey
        fields = [
            "id",
            "project",
            "title",
            "description",
            "survey_type",
            "status",
            "questions",
            "response_count",
            "submitted_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_response_count(self, obj):
        return obj.responses.count()

    def get_submitted_count(self, obj):
        return obj.responses.filter(submitted=True).count()


class ImpactProjectSerializer(serializers.ModelSerializer):
    surveys = ImpactSurveySerializer(many=True, read_only=True)

    class Meta:
        model = ImpactProject
        fields = [
            "id",
            "client_organisation",
            "client_name",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "target_respondents",
            "surveys",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "client_name", "created_at", "updated_at"]


class ImpactProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactProject
        fields = [
            "id",
            "client_organisation",
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "target_respondents",
        ]
        read_only_fields = ["id"]


class ImpactResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactResponse
        fields = [
            "id",
            "survey",
            "respondent_name",
            "respondent_phone",
            "answers",
            "submitted",
            "submitted_at",
            "created_at",
        ]
        read_only_fields = ["id", "submitted", "submitted_at", "created_at"]


class ImpactSurveyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactSurvey
        fields = [
            "id",
            "title",
            "description",
            "survey_type",
            "status",
            "questions",
        ]
        read_only_fields = ["id"]


class ImpactSubmitSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.DictField())
    respondent_name = serializers.CharField(required=False, allow_blank=True)
    respondent_phone = serializers.CharField(required=False, allow_blank=True)