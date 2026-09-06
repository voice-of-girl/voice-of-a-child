"""Serializers for the accounts app."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    # Names are useful but not essential for provisioning; allow accounts to
    # be created with just email + role + organisation (+ password).
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)

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

        # Accounts are provisioned by the platform admin. Organisations never
        # create their own users. This guard is defence in depth alongside the
        # IsPlatformAdmin permission on every creation endpoint.
        if user.role != PLATFORM_ADMIN:
            raise serializers.ValidationError(
                {"detail": "Only the platform admin can create user accounts."}
            )

        # Every role except platform admin must be bound to a tenant.
        if requested_role != PLATFORM_ADMIN and requested_org is None:
            raise serializers.ValidationError(
                {"organisation": "An organisation is required for this role."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return CustomUser.objects.create_user(password=password, **validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)


class VoiceTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT obtain-payload that also returns the authenticated user.

    Returning the user object on login lets the frontend route by role and
    hydrate its session in a single round-trip.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["name"] = user.full_name
        token["role"] = user.role
        return token

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs["user"] = MeSerializer(self.user, context=self.context).data
        return attrs