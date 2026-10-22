from rest_framework import generics, permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Emails are stored lowercased at registration, so match case-insensitively at login too.
        attrs[self.username_field] = attrs[self.username_field].lower()
        return super().validate(attrs)


class LoginView(TokenObtainPairView):
    """Takes `email` + `password`, returns `access` and `refresh` JWTs."""

    serializer_class = LoginSerializer
