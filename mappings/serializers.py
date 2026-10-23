from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from patients.models import Patient

from .models import PatientDoctorMapping


class OwnPatientField(serializers.PrimaryKeyRelatedField):
    """Only accept patients created by the requesting user."""

    def get_queryset(self):
        return Patient.objects.owned_by(self.context["request"].user)


class MappingSerializer(serializers.ModelSerializer):
    patient = OwnPatientField()
    patient_name = serializers.ReadOnlyField(source="patient.name")
    doctor_name = serializers.ReadOnlyField(source="doctor.name")
    doctor_specialization = serializers.ReadOnlyField(source="doctor.specialization")

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id", "patient", "patient_name", "doctor", "doctor_name",
            "doctor_specialization", "notes", "created_at",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=PatientDoctorMapping.objects.all(),
                fields=("patient", "doctor"),
                message="This doctor is already assigned to this patient.",
            )
        ]
