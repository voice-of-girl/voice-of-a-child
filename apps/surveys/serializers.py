from rest_framework import serializers

from apps.participants.models import Participant
from apps.participants.serializers import ParticipantSerializer
from apps.programmes.models import Programme
from apps.surveys.models import (
    Answer,
    Question,
    Survey,
    SurveyAssignment,
    SurveyResponse,
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "help_text",
            "question_type",
            "required",
            "options",
            "order",
        ]
        read_only_fields = ["id"]


class QuestionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "help_text",
            "question_type",
            "required",
            "options",
            "order",
        ]
        read_only_fields = ["id"]


class SurveyAssignmentSerializer(serializers.ModelSerializer):
    participant = ParticipantSerializer(read_only=True)

    class Meta:
        model = SurveyAssignment
        fields = ["id", "survey", "participant", "programme", "assigned_at", "due_date"]
        read_only_fields = ["id", "assigned_at"]


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    assignments = SurveyAssignmentSerializer(many=True, read_only=True)
    response_count = serializers.IntegerField(read_only=True)
    submitted_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "organisation",
            "programme",
            "title",
            "description",
            "survey_type",
            "status",
            "questions",
            "assignments",
            "response_count",
            "submitted_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SurveyWriteSerializer(serializers.ModelSerializer):
    questions = QuestionWriteSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = [
            "id",
            "programme",
            "title",
            "description",
            "survey_type",
            "status",
            "questions",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        survey = Survey.objects.create(**validated_data)
        for idx, q in enumerate(questions_data):
            Question.objects.create(survey=survey, order=idx, **q)
        return survey

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", None)
        if questions_data is not None:
            instance.questions.all().delete()
            for idx, q in enumerate(questions_data):
                Question.objects.create(survey=instance, order=idx, **q)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SurveyAssignSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    programme_id = serializers.IntegerField(required=False)
    due_date = serializers.DateTimeField(required=False, allow_null=True)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "response", "question", "value"]
        read_only_fields = ["id"]


class SurveyResponseSerializer(serializers.ModelSerializer):
    participant = ParticipantSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            "id",
            "survey",
            "participant",
            "organisation",
            "access_token",
            "submitted",
            "submitted_at",
            "created_at",
            "answers",
        ]
        read_only_fields = ["id", "access_token", "created_at"]


class PublicAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    value = serializers.JSONField()


class PublicSurveySubmitSerializer(serializers.Serializer):
    answers = PublicAnswerInputSerializer(many=True)
    respondent_name = serializers.CharField(required=False, allow_blank=True)
    respondent_phone = serializers.CharField(required=False, allow_blank=True)


class PublicSurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ["id", "title", "description", "survey_type", "questions"]