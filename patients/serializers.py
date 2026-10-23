from django.utils import timezone
from rest_framework import serializers

from config.serializers import StrictFieldsMixin

from .models import Patient


class PatientSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.email")
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "date_of_birth",
            "age",
            "gender",
            "phone",
            "email",
            "address",
            "medical_history",
            "created_by",
            "created_at",
            "updated_at",
        )

    def get_age(self, obj) -> int:
        today, dob = timezone.localdate(), obj.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def validate_date_of_birth(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
