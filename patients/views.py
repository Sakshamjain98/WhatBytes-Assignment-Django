from rest_framework import viewsets

from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD for patients. Users only ever see patients they created (others get 404)."""

    serializer_class = PatientSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]
    lookup_value_converter = "int"

    def get_queryset(self):
        return Patient.objects.owned_by(self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
