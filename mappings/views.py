from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import MappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    """GET: all mappings for the user's patients. POST: assign a doctor to one of the user's patients."""

    serializer_class = MappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.owned_by(self.request.user)


class MappingDetailView(APIView):
    """
    The spec puts two different ids on the same URL:
      GET    /api/mappings/<patient_id>/  -> doctors assigned to that patient
      DELETE /api/mappings/<mapping_id>/  -> remove that mapping
    """

    @extend_schema(
        operation_id="mappings_patient_doctors",
        summary="Doctors assigned to a patient",
        parameters=[OpenApiParameter("pk", int, OpenApiParameter.PATH, description="Patient id")],
        responses=DoctorSerializer(many=True),
    )
    def get(self, request, pk):
        patient = get_object_or_404(Patient.objects.owned_by(request.user), pk=pk)
        doctors = Doctor.objects.filter(patient_mappings__patient=patient).select_related("created_by")
        return Response(DoctorSerializer(doctors, many=True).data)

    @extend_schema(
        summary="Remove a doctor from a patient",
        parameters=[OpenApiParameter("pk", int, OpenApiParameter.PATH, description="Mapping id")],
        responses={204: None},
    )
    def delete(self, request, pk):
        get_object_or_404(PatientDoctorMapping.objects.owned_by(request.user), pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
