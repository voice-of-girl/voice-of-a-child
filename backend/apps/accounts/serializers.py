"""Serializers for the accounts app."""
from rest_framework import serializers

from apps.core.permissions import PLATFORM_ADMIN, ORGANISATION_ADMIN
from apps.organisations.models import Organisation
from apps.organisations.serializers import OrganisationBriefSerializer

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.name", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "role",
            "organisation",
            "organisation_name",
            "is_active",
            "is_staff",
            "created_at",
        ]
        read_only_fields = ["id", "is_staff", "created_at"]


class MeSerializer(serializers.ModelSerializer):
    organisation = OrganisationBriefSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "role",
            "organisation",
            "is_active",
            "created_at",
        ]


class RegisterUserSerializer(serializers.ModelSerializer):
    """Creates a user. Used by platform admins (and org admins for their org)."""

    password = serializers.CharField(
        write_only=True, min_length=8, max_length=128, style={"input_type": "password"}
    )
    organisation = serializers.PrimaryKeyRelatedField(
        queryset=Organisation.objects.none(), required=False, allow_null=True
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "organisation",
            "password",
            "is_active",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The queryset depends on the authenticated user's permissions.
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            org_qs = request.user.organisations_visible()
            self.fields["organisation"].queryset = org_qs

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        requested_role = attrs.get("role", CustomUser.Role.STAFF)
        requested_org = attrs.get("organisation")

        if user.role != PLATFORM_ADMIN:
            # Org admins may only create staff within their own organisation.
            if requested_org is not None and requested_org.pk != user.organisation_id:
                raise serializers.ValidationError(
                    {"organisation": "You cannot create users in another organisation."}
                )
            if requested_role == PLATFORM_ADMIN:
                raise serializers.ValidationError(
                    {"role": "Only platform admins can create platform admins."}
                )
            attrs["organisation"] = user.organisation
            if user.role == ORGANISATION_ADMIN:
                allowed = {CustomUser.Role.PROGRAMME_MANAGER, CustomUser.Role.MONITORING_OFFICER, CustomUser.Role.STAFF}
                if requested_role not in allowed:
                    raise serializers.ValidationError(
                        {"role": f"Organisation admins may only assign {sorted(r for r in allowed)} roles."}
                    )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return CustomUser.objects.create_user(password=password, **validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)