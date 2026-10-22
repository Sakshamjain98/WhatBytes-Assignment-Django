from django.utils import timezone
from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = Patient
        fields = (
            "id", "name", "date_of_birth", "gender", "phone", "email",
            "address", "medical_history", "created_by", "created_at", "updated_at",
        )

    def validate_date_of_birth(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
