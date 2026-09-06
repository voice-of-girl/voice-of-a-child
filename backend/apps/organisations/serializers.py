"""Serializers for the organisations app."""
from rest_framework import serializers

from .models import Organisation


class OrganisationBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["id", "name", "organisation_type", "verification_status"]


class OrganisationSerializer(serializers.ModelSerializer):
    programmes_count = serializers.IntegerField(read_only=True, default=0)
    participants_count = serializers.IntegerField(read_only=True, default=0)
    surveys_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Organisation
        fields = [
            "id",
            "name",
            "description",
            "organisation_type",
            "email",
            "phone_number",
            "website",
            "address",
            "district",
            "country",
            "verification_status",
            "programmes_count",
            "participants_count",
            "surveys_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]