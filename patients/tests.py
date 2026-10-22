from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Patient

User = get_user_model()

PATIENT = {"name": "Ravi Kumar", "date_of_birth": "1990-05-14", "gender": "male", "phone": "+919876543210"}


class PatientTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@example.com", name="A", password="Str0ng-pass!")
        self.other = User.objects.create_user(email="b@example.com", name="B", password="Str0ng-pass!")
        self.client.force_authenticate(self.user)

    def test_crud(self):
        res = self.client.post("/api/patients/", PATIENT)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["created_by"], "a@example.com")
        url = f"/api/patients/{res.data['id']}/"

        self.assertEqual(self.client.get("/api/patients/").data["count"], 1)
        self.assertEqual(self.client.get(url).data["name"], "Ravi Kumar")

        res = self.client.put(url, {**PATIENT, "name": "Ravi K."})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Ravi K.")

        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.exists())

    def test_validation(self):
        res = self.client.post("/api/patients/", {**PATIENT, "date_of_birth": "2999-01-01", "gender": "x", "phone": "abc"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(res.data), {"date_of_birth", "gender", "phone"})

    def test_cannot_see_or_touch_other_users_patients(self):
        theirs = Patient.objects.create(created_by=self.other, **PATIENT)
        url = f"/api/patients/{theirs.id}/"
        self.assertEqual(self.client.get("/api/patients/").data["count"], 0)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.put(url, PATIENT).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post("/api/patients/", PATIENT).status_code, status.HTTP_401_UNAUTHORIZED)
