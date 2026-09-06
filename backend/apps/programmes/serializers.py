"""Serializers for programmes."""
from rest_framework import serializers

from .models import Programme


class ProgrammeSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.name", read_only=True)
    participant_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Programme
        fields = [
            "id",
            "organisation",
            "organisation_name",
            "name",
            "description",
            "category",
            "location",
            "start_date",
            "end_date",
            "status",
            "target_participants",
            "participant_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation", "created_at", "updated_at"]