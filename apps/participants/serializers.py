from rest_framework import serializers

from apps.participants.models import Participant


class ParticipantSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    organisation_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Participant
        fields = [
            "id",
            "organisation_id",
            "full_name",
            "date_of_birth",
            "age",
            "gender",
            "phone_number",
            "email",
            "district",
            "region",
            "country",
            "education_level",
            "skills",
            "interests",
            "career_goals",
            "employment_status",
            "registration_source",
            "verification_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParticipantWriteSerializer(serializers.ModelSerializer):
    """Accept age as an alternative to date_of_birth on write."""

    age = serializers.IntegerField(required=False, write_only=True, min_value=5, max_value=100)

    class Meta:
        model = Participant
        fields = [
            "id",
            "full_name",
            "date_of_birth",
            "age",
            "gender",
            "phone_number",
            "email",
            "district",
            "region",
            "country",
            "education_level",
            "skills",
            "interests",
            "career_goals",
            "employment_status",
            "registration_source",
            "verification_status",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        import datetime

        dob = attrs.get("date_of_birth")
        age = attrs.get("age")
        if not dob and age:
            year = datetime.date.today().year - age
            attrs["date_of_birth"] = datetime.date(year, 1, 1)
        if not attrs.get("date_of_birth") and not attrs.get("age"):
            raise serializers.ValidationError(
                {"date_of_birth": "Either date_of_birth or age is required."}
            )
        return attrs

    def validate_phone_number(self, value):
        if not value:
            return value
        # Duplicate detection: within the same organisation (or globally when org-less).
        org_id = self.context.get("organisation_id")
        qs = Participant.objects.filter(phone_number=value)
        if org_id:
            qs = qs.filter(organisation_id=org_id)
        else:
            qs = qs.filter(organisation_id__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A participant with this phone number already exists.")
        return value

    def validate_email(self, value):
        if not value:
            return value
        org_id = self.context.get("organisation_id")
        qs = Participant.objects.filter(email=value)
        if org_id:
            qs = qs.filter(organisation_id=org_id)
        else:
            qs = qs.filter(organisation_id__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A participant with this email already exists.")
        return value


class ParticipantVerifySerializer(serializers.Serializer):
    verification_status = serializers.ChoiceField(
        choices=Participant.VerificationStatus.choices
    )
    note = serializers.CharField(required=False, allow_blank=True)


class ParticipantClaimSerializer(serializers.Serializer):
    organisation_id = serializers.IntegerField()