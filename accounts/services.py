from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer


def auth_response(user):
    """The register/login payload: the user plus a fresh JWT pair."""
    refresh = RefreshToken.for_user(user)
    return {"user": UserSerializer(user).data, "access": str(refresh.access_token), "refresh": str(refresh)}
