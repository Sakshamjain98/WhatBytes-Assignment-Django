from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from config.serializers import StrictFieldsMixin

from .serializers import AuthResponseSerializer, RegisterSerializer
from .services import auth_response


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(responses={201: AuthResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(auth_response(serializer.save()), status=status.HTTP_201_CREATED)


class LoginSerializer(StrictFieldsMixin, TokenObtainPairSerializer):
    def validate(self, attrs):
        # Emails are stored lowercased at registration, so match case-insensitively at login too.
        attrs[self.username_field] = attrs[self.username_field].lower()
        super().validate(attrs)  # authenticates and sets self.user
        return auth_response(self.user)


class LoginView(TokenObtainPairView):
    """Takes `email` + `password`, returns the user plus `access` and `refresh` JWTs."""

    serializer_class = LoginSerializer
    throttle_scope = "auth"
    throttle_classes = [ScopedRateThrottle]

    @extend_schema(responses={200: AuthResponseSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
