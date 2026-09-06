from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organisations.models import Organisation

User = get_user_model()


class OrganisationBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["id", "name", "organisation_type", "status"]


class UserSerializer(serializers.ModelSerializer):
    organisation = OrganisationBriefSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "organisation",
            "is_active",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OrganisationalUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    organisation_id = serializers.PrimaryKeyRelatedField(
        source="organisation", queryset=Organisation.objects.all()
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "organisation_id",
            "is_active",
        ]

    def validate(self, attrs):
        attrs.setdefault("role", User.Role.ORGANISATION)
        attrs["role"] = User.Role.ORGANISATION
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_verified = False
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)