from rest_framework import serializers

from apps.participants.models import Participant
from apps.participants.serializers import ParticipantSerializer
from apps.programmes.models import (
    Programme,
    ProgrammeEnrollment,
    ProgrammeKPI,
    ProgrammeObjective,
)


class ProgrammeObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeObjective
        fields = ["id", "title", "detail", "order"]


class ProgrammeEnrollmentCreateSerializer(serializers.Serializer):
    participant_id = serializers.PrimaryKeyRelatedField(
        queryset=Participant.objects.all(), source="participant"
    )
    status = serializers.ChoiceField(
        choices=ProgrammeEnrollment.Status.choices, default=ProgrammeEnrollment.Status.ENROLLED
    )

    def validate_participant_id(self, participant):
        # NOTE: hook must match the field name (participant_id), not the source.
        programme = self.context.get("programme")
        if (
            programme is not None
            and programme.organisation_id is not None
            and participant.organisation_id is not None
            and participant.organisation_id != programme.organisation_id
        ):
            raise serializers.ValidationError(
                "Participant does not belong to this programme's organisation."
            )
        return participant


class ProgrammeEnrollmentSerializer(serializers.ModelSerializer):
    participant = ParticipantSerializer(read_only=True)

    class Meta:
        model = ProgrammeEnrollment
        fields = [
            "id",
            "programme",
            "participant",
            "status",
            "progress",
            "enrolled_at",
            "completed_at",
            "outcome_notes",
        ]
        read_only_fields = ["id", "programme", "enrolled_at"]


class ProgrammeKPISerializer(serializers.ModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)
    percentage_change = serializers.FloatField(read_only=True)
    percentage_point_change = serializers.FloatField(read_only=True)

    class Meta:
        model = ProgrammeKPI
        fields = [
            "id",
            "programme",
            "name",
            "description",
            "category",
            "unit",
            "target_value",
            "current_value",
            "baseline_value",
            "measurement_frequency",
            "progress_percentage",
            "percentage_change",
            "percentage_point_change",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "programme", "created_at", "updated_at"]


class ProgrammeSerializer(serializers.ModelSerializer):
    objectives = ProgrammeObjectiveSerializer(many=True, read_only=True)
    kpis = ProgrammeKPISerializer(many=True, read_only=True)
    participants_count = serializers.IntegerField(read_only=True)
    active_count = serializers.IntegerField(read_only=True)
    completed_count = serializers.IntegerField(read_only=True)
    dropped_out_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Programme
        fields = [
            "id",
            "organisation",
            "title",
            "description",
            "category",
            "location",
            "start_date",
            "end_date",
            "status",
            "target_participants",
            "objectives",
            "kpis",
            "participants_count",
            "active_count",
            "completed_count",
            "dropped_out_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProgrammeWriteSerializer(serializers.ModelSerializer):
    objectives = ProgrammeObjectiveSerializer(many=True, required=False)

    class Meta:
        model = Programme
        fields = [
            "id",
            "title",
            "description",
            "category",
            "location",
            "start_date",
            "end_date",
            "status",
            "target_participants",
            "objectives",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        objectives_data = validated_data.pop("objectives", [])
        # perform_create() may already inject organisation_id via save().
        organisation_id = validated_data.pop("organisation_id", None) or self.context.get(
            "organisation_id"
        )
        created_by = self.context.get("created_by")
        programme = Programme.objects.create(
            **validated_data, organisation_id=organisation_id, created_by=created_by
        )
        for idx, obj in enumerate(objectives_data):
            ProgrammeObjective.objects.create(programme=programme, order=idx, **obj)
        return programme

    def update(self, instance, validated_data):
        objectives_data = validated_data.pop("objectives", None)
        if objectives_data is not None:
            instance.objectives.all().delete()
            for idx, obj in enumerate(objectives_data):
                ProgrammeObjective.objects.create(programme=instance, order=idx, **obj)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance