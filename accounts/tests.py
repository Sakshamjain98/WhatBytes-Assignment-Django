from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    register_url = "/api/auth/register/"
    login_url = "/api/auth/login/"

    def test_register_creates_user_and_hides_password(self):
        res = self.client.post(self.register_url, {"name": "Asha", "email": "Asha@Example.com", "password": "Str0ng-pass!"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", res.data)
        self.assertEqual(res.data["email"], "asha@example.com")
        self.assertTrue(User.objects.get(email="asha@example.com").check_password("Str0ng-pass!"))

    def test_register_rejects_duplicate_email_and_weak_password(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        res = self.client.post(self.register_url, {"name": "A", "email": "ASHA@example.com", "password": "Str0ng-pass!"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", res.data)

        res = self.client.post(self.register_url, {"name": "B", "email": "b@example.com", "password": "123"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)

    def test_register_requires_all_fields(self):
        res = self.client.post(self.register_url, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(res.data), {"name", "email", "password"})

    def test_login_returns_jwt_pair(self):
        User.objects.create_user(email="asha@example.com", name="Asha", password="Str0ng-pass!")
        res = self.client.post(self.login_url, {"email": "ASHA@example.com", "password": "Str0ng-pass!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

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
