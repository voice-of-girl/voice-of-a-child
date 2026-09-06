"""Serializers for surveys, questions and responses."""
from django.conf import settings
from rest_framework import serializers

from .models import Survey, SurveyAnswer, SurveyQuestion, SurveyResponse


def _question_fields(order, qdata):
    return {
        "question": (qdata.get("question") or "Untitled question")[:500],
        "help_text": (qdata.get("help_text") or "")[:300],
        "question_type": qdata.get("question_type") or SurveyQuestion.QuestionType.SHORT_TEXT,
        "options": qdata.get("options") or [],
        "required": qdata.get("required", True),
        "order": qdata.get("order") or (order + 1),
        "validation_rules": qdata.get("validation_rules") or {},
    }


class SurveyQuestionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = [
            "id",
            "question",
            "help_text",
            "question_type",
            "options",
            "required",
            "order",
            "validation_rules",
        ]


class SurveySerializer(serializers.ModelSerializer):
    questions = SurveyQuestionSerializer(many=True, required=False)
    organisation_name = serializers.CharField(source="organisation.name", read_only=True)
    programme_name = serializers.CharField(
        source="programme.name", read_only=True, default=None
    )
    project_name = serializers.CharField(
        source="impact_project.name", read_only=True, default=None
    )
    responses_count = serializers.SerializerMethodField()
    public_url = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            "id",
            "organisation",
            "organisation_name",
            "programme",
            "programme_name",
            "impact_project",
            "project_name",
            "title",
            "description",
            "stage",
            "status",
            "public_token",
            "public_url",
            "start_date",
            "end_date",
            "allow_multiple_responses",
            "thank_you_message",
            "responses_count",
            "questions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organisation",
            "public_token",
            "responses_count",
            "created_at",
            "updated_at",
        ]

    def get_responses_count(self, obj):
        """Prefer the annotated count from the queryset; fall back to a query."""
        annotated = getattr(obj, "responses_count", None)
        if annotated is not None:
            return annotated
        return obj.responses.count()

    def get_public_url(self, obj):
        return f"{settings.PUBLIC_SURVEY_BASE_URL}/public/surveys/{obj.public_token}"

    def validate(self, attrs):
        programme = attrs.get("programme") or getattr(self.instance, "programme", None)
        impact_project = attrs.get("impact_project") or getattr(self.instance, "impact_project", None)
        organisation = self.context["request"].user.organisation
        if programme and programme.organisation_id != organisation.id:
            raise serializers.ValidationError({"programme": "Programme does not belong to your organisation."})
        if impact_project and impact_project.organisation_id != organisation.id:
            raise serializers.ValidationError({"impact_project": "Impact project does not belong to your organisation."})
        qdata = attrs.get("questions")
        if qdata is not None:
            question_types = {c[0] for c in SurveyQuestion.QuestionType.choices}
            for q in qdata:
                if q.get("question_type") not in question_types:
                    raise serializers.ValidationError({"questions": f"Invalid question_type: {q.get('question_type')}"})
        return attrs

    def create(self, validated_data):
        questions = validated_data.pop("questions", None) or []
        survey = Survey.objects.create(**validated_data)
        for index, qdata in enumerate(questions):
            SurveyQuestion.objects.create(survey=survey, **_question_fields(index, qdata))
        return survey

    def update(self, instance, validated_data):
        questions = validated_data.pop("questions", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions is not None:
            instance.questions.all().delete()
            for index, qdata in enumerate(questions):
                SurveyQuestion.objects.create(survey=instance, **_question_fields(index, qdata))
        return instance
class SurveyAnswerReadSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source="question.question", read_only=True)
    question_type = serializers.CharField(source="question.question_type", read_only=True)
    order = serializers.IntegerField(source="question.order", read_only=True)

    class Meta:
        model = SurveyAnswer
        fields = ["id", "question", "question_type", "order", "value"]


class SurveyResponseSerializer(serializers.ModelSerializer):
    survey_title = serializers.CharField(source="survey.title", read_only=True)
    programme_name = serializers.CharField(
        source="programme.name", read_only=True, default=None
    )
    participant_name = serializers.CharField(
        source="participant.name", read_only=True, default=None
    )
    answers = SurveyAnswerReadSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            "id",
            "survey",
            "survey_title",
            "programme",
            "programme_name",
            "participant",
            "participant_name",
            "respondent_name",
            "respondent_email",
            "status",
            "submitted_at",
            "metadata",
            "answers",
        ]
        read_only_fields = ["id", "status", "submitted_at"]


class PublicSurveySerializer(serializers.ModelSerializer):
    """Exactly what an anonymous respondent needs — nothing sensitive."""

    questions = SurveyQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ["id", "title", "description", "stage", "questions", "thank_you_message"]
        read_only_fields = fields


class PublicResponseSerializer(serializers.Serializer):
    """
    Accepts an anonymous survey submission.

    Only whitelisted fields are accepted (defence against mass assignment).
    """

    respondent_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    respondent_email = serializers.EmailField(required=False, allow_blank=True)
    answers = serializers.JSONField(required=True)
    # Honeypot field: real users never see it; bots that fill it are dropped.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)