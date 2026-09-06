"""Monitoring serializers."""
from django.utils import timezone
from rest_framework import serializers

from .models import Challenge, Feedback, SupportRequest


class ChallengeSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True, default=None
    )
    participant_name = serializers.CharField(
        source="participant.name", read_only=True, default=None
    )
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            "id",
            "organisation",
            "programme",
            "programme_name",
            "participant",
            "participant_name",
            "category",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "assigned_to_name",
            "resolution_notes",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "resolved_at", "created_at", "updated_at"]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.full_name
        return None

    def update(self, instance, validated_data):
        if "status" in validated_data:
            if validated_data["status"] == Challenge.Status.RESOLVED and not instance.resolved_at:
                validated_data["resolved_at"] = timezone.now()
            elif validated_data["status"] != Challenge.Status.RESOLVED:
                validated_data["resolved_at"] = None
        return super().update(instance, validated_data)


class FeedbackSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True, default=None
    )
    participant_name = serializers.CharField(
        source="participant.name", read_only=True, default=None
    )

    class Meta:
        model = Feedback
        fields = [
            "id",
            "organisation",
            "programme",
            "programme_name",
            "participant",
            "participant_name",
            "category",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]


class SupportRequestSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(
        source="programme.name", read_only=True, default=None
    )
    participant_name = serializers.CharField(
        source="participant.name", read_only=True, default=None
    )
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = SupportRequest
        fields = [
            "id",
            "organisation",
            "programme",
            "programme_name",
            "participant",
            "participant_name",
            "category",
            "description",
            "status",
            "assigned_to",
            "assigned_to_name",
            "resolution_notes",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "resolved_at", "created_at", "updated_at"]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.full_name
        return None

    def update(self, instance, validated_data):
        if "status" in validated_data:
            if (
                validated_data["status"] in (SupportRequest.Status.RESOLVED, SupportRequest.Status.CLOSED)
                and not instance.resolved_at
            ):
                validated_data["resolved_at"] = timezone.now()
        return super().update(instance, validated_data)