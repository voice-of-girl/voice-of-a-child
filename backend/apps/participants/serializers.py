"""Participant serializers."""
from rest_framework import serializers

from .models import Participant


class ParticipantSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.name", read_only=True)
    programme_name = serializers.CharField(source="programme.name", read_only=True, default=None)

    class Meta:
        model = Participant
        fields = [
            "id",
            "organisation",
            "organisation_name",
            "programme",
            "programme_name",
            "name",
            "email",
            "phone",
            "external_reference",
            "gender",
            "date_of_birth",
            "age",
            "location",
            "district",
            "status",
            "enrolled_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]

    def validate_programme(self, value):
        """A participant may only be attached to a programme in the same organisation."""
        request = self.context.get("request")
        if value and request and request.user.is_authenticated:
            if not request.user.is_platform_admin and value.organisation_id != request.user.organisation_id:
                raise serializers.ValidationError(
                    "Programme does not belong to your organisation."
                )
        return value


class ParticipantBulkImportSerializer(serializers.ModelSerializer):
    """Bulk import participants by external reference to avoid duplication."""

    class Meta:
        model = Participant
        fields = [
            "id",
            "programme",
            "name",
            "email",
            "phone",
            "external_reference",
            "gender",
            "age",
            "location",
            "district",
            "status",
        ]
        read_only_fields = ["id"]