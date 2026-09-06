from rest_framework import serializers

from apps.organisations.models import Organisation


class OrganisationSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(source="users.count", read_only=True)

    class Meta:
        model = Organisation
        fields = [
            "id",
            "name",
            "organisation_type",
            "contact_person",
            "email",
            "phone_number",
            "website",
            "address",
            "district",
            "country",
            "status",
            "user_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganisationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Organisation.Status.choices)