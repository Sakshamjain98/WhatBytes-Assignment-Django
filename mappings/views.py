from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import MappingSerializer


def user_mappings(user):
    return PatientDoctorMapping.objects.filter(patient__created_by=user).select_related("patient", "doctor")


class MappingListCreateView(generics.ListCreateAPIView):
    """GET: all mappings for the user's patients. POST: assign a doctor to one of the user's patients."""

    serializer_class = MappingSerializer

    def get_queryset(self):
        return user_mappings(self.request.user)


class MappingDetailView(APIView):
    """
    The spec puts two different ids on the same URL:
      GET    /api/mappings/<patient_id>/  -> doctors assigned to that patient
      DELETE /api/mappings/<mapping_id>/  -> remove that mapping
    """

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        doctors = Doctor.objects.filter(patient_mappings__patient=patient).select_related("created_by")
        return Response(DoctorSerializer(doctors, many=True).data)

    def delete(self, request, pk):
        get_object_or_404(user_mappings(request.user), pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
