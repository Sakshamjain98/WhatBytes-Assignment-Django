from rest_framework import permissions, viewsets

from .models import Doctor
from .permissions import IsCreatorOrReadOnly
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """Doctors are a shared directory: everyone can list them, only the creator can edit/delete."""

    queryset = Doctor.objects.select_related("created_by")
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
