from rest_framework import serializers

from config.serializers import StrictFieldsMixin

from .models import Doctor


class DoctorSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "specialization",
            "email",
            "phone",
            "experience_years",
            "created_by",
            "created_at",
            "updated_at",
        )
