from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from config.tests import error_fields

from .models import Doctor

User = get_user_model()

DOCTOR = {
    "name": "Meera Shah",
    "specialization": "Cardiology",
    "email": "meera@clinic.com",
    "phone": "9876500000",
    "experience_years": 12,
}


class DoctorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@example.com", name="A", password="Str0ng-pass!")
        self.other = User.objects.create_user(email="b@example.com", name="B", password="Str0ng-pass!")
        self.client.force_authenticate(self.user)

    def test_crud(self):
        res = self.client.post("/api/doctors/", DOCTOR)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        url = f"/api/doctors/{res.data['id']}/"

        self.assertEqual(self.client.get(url).data["specialization"], "Cardiology")
        res = self.client.put(url, {**DOCTOR, "experience_years": 13})
        self.assertEqual(res.data["experience_years"], 13)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.exists())

    def test_validation(self):
        self.client.post("/api/doctors/", DOCTOR)
        res = self.client.post("/api/doctors/", {**DOCTOR, "experience_years": 200, "phone": "12"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_fields(res), {"email", "experience_years", "phone"})

    def test_all_doctors_visible_but_only_creator_can_modify(self):
        theirs = Doctor.objects.create(created_by=self.other, **DOCTOR)
        url = f"/api/doctors/{theirs.id}/"
        self.assertEqual(self.client.get("/api/doctors/").data["meta"]["total"], 1)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.put(url, DOCTOR).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)
