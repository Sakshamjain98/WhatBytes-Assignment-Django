from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from config.exceptions import Conflict
from config.serializers import StrictFieldsMixin

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "email")


class RegisterSerializer(StrictFieldsMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "name", "email", "password")
        # Duplicate emails are a 409 (see validate_email), not the default 400 unique validator.
        extra_kwargs = {"email": {"validators": []}}

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise Conflict("A user with this email already exists.")
        return value

    def validate(self, attrs):
        validate_password(attrs["password"], user=User(name=attrs["name"], email=attrs["email"]))
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AuthResponseSerializer(serializers.Serializer):
    """Response DTO for register and login (documentation only)."""

    user = UserSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()
