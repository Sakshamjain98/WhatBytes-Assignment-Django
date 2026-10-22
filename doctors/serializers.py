from rest_framework import serializers

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = Doctor
        fields = (
            "id", "name", "specialization", "email", "phone",
            "experience_years", "created_by", "created_at", "updated_at",
        )
