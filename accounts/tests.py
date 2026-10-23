from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from config.tests import error_fields

from .services import auth_response

User = get_user_model()


class AuthTests(APITestCase):
    register_url = "/api/auth/register/"
    login_url = "/api/auth/login/"

    def setUp(self):
        cache.clear()  # throttle counters are cached and would leak between tests

    def test_register_creates_user_and_hides_password(self):
        res = self.client.post(self.register_url, {"name": "Asha", "email": "Asha@Example.com", "password": "Str0ng-pass!"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(res.data), {"user", "access", "refresh"})
        self.assertEqual(set(res.data["user"]), {"id", "name", "email"})
        self.assertEqual(res.data["user"]["email"], "asha@example.com")
        self.assertTrue(User.objects.get(email="asha@example.com").check_password("Str0ng-pass!"))

    def test_register_rejects_duplicate_email_and_weak_password(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        res = self.client.post(self.register_url, {"name": "A", "email": "ASHA@example.com", "password": "Str0ng-pass!"})
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data["error"]["code"], "CONFLICT")

        res = self.client.post(self.register_url, {"name": "B", "email": "b@example.com", "password": "123"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_fields(res), {None})  # password rules are object-level errors

    def test_register_requires_all_fields(self):
        res = self.client.post(self.register_url, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_fields(res), {"name", "email", "password"})

    def test_login_returns_jwt_pair(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        res = self.client.post(self.login_url, {"email": "ASHA@example.com", "password": "Str0ng-pass!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(set(res.data), {"user", "access", "refresh"})
        self.assertEqual(res.data["user"]["email"], "asha@example.com")

    def test_login_wrong_password(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        res = self.client.post(self.login_url, {"email": "asha@example.com", "password": "nope"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_authenticates_protected_endpoint(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        token = self.client.post(self.login_url, {"email": "asha@example.com", "password": "Str0ng-pass!"}).data["access"]
        self.assertEqual(self.client.get("/api/patients/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.get("/api/patients/").status_code, status.HTTP_200_OK)

    def test_logout_blacklists_refresh_token(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        refresh = self.client.post(self.login_url, {"email": "asha@example.com", "password": "Str0ng-pass!"}).data["refresh"]
        self.assertEqual(self.client.post("/api/auth/logout/", {"refresh": refresh}).status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post("/api/auth/token/refresh/", {"refresh": refresh}).status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_auth_endpoints_are_rate_limited(self):
        # default AUTH_THROTTLE_RATE is 10/min
        codes = [self.client.post(self.login_url, {"email": "x@example.com", "password": "x"}).status_code for _ in range(11)]
        self.assertEqual(codes[:10], [status.HTTP_401_UNAUTHORIZED] * 10)
        self.assertEqual(codes[10], status.HTTP_429_TOO_MANY_REQUESTS)


class AuthServiceTests(APITestCase):
    def test_auth_response_issues_tokens_for_that_user(self):
        user = User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        payload = auth_response(user)
        self.assertEqual(payload["user"], {"id": user.id, "name": "Asha", "email": "asha@example.com"})
        self.assertEqual(int(AccessToken(payload["access"])["user_id"]), user.id)
