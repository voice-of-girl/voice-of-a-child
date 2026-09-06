from rest_framework import serializers

from apps.monitoring.models import Challenge


class ChallengeSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(source="participant.full_name", read_only=True)
    programme_title = serializers.CharField(source="programme.title", read_only=True)

    class Meta:
        model = Challenge
        fields = [
            "id",
            "organisation",
            "programme",
            "programme_title",
            "participant",
            "participant_name",
            "category",
            "description",
            "status",
            "date_reported",
            "date_resolved",
            "resolution_notes",
        ]
        read_only_fields = ["id", "date_reported", "date_resolved"]


class ChallengeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            "id",
            "programme",
            "participant",
            "category",
            "description",
            "status",
            "resolution_notes",
        ]
        read_only_fields = ["id"]

    def validate_programme(self, value):
        if value and value.organisation_id != self.context.get("organisation_id"):
            raise serializers.ValidationError("Programme does not belong to this organisation.")
        return value

    def validate_participant(self, value):
        if value and value.organisation_id and value.organisation_id != self.context.get("organisation_id"):
            raise serializers.ValidationError("Participant does not belong to this organisation.")
        return value


class ChallengeResolveSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(required=False, allow_blank=True)