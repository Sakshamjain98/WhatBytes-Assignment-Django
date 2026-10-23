from rest_framework import serializers

from config.serializers import StrictFieldsMixin
from doctors.serializers import DoctorSerializer
from patients.models import Patient

from .models import PatientDoctorMapping
from .services import assign_doctor


class OwnPatientField(serializers.PrimaryKeyRelatedField):
    """Only accept patients created by the requesting user."""

    def get_queryset(self):
        return Patient.objects.owned_by(self.context["request"].user)


class MappingSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    patient = OwnPatientField()
    patient_name = serializers.ReadOnlyField(source="patient.name")
    doctor_name = serializers.ReadOnlyField(source="doctor.name")
    doctor_specialization = serializers.ReadOnlyField(source="doctor.specialization")

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "doctor_specialization",
            "notes",
            "created_at",
        )
        validators = []  # duplicates are a 409 from services.assign_doctor, not a 400 here

    def create(self, validated_data):
        return assign_doctor(**validated_data)


class AssignedDoctorSerializer(DoctorSerializer):
    """A doctor as seen from a patient: the doctor plus the mapping id (for DELETE) and when it was assigned."""

    mapping_id = serializers.IntegerField(read_only=True)
    assigned_at = serializers.DateTimeField(read_only=True)

    class Meta(DoctorSerializer.Meta):
        fields = DoctorSerializer.Meta.fields + ("mapping_id", "assigned_at")
