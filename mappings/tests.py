from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from patients.models import Patient

from .models import PatientDoctorMapping

User = get_user_model()


class MappingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@example.com", name="A", password="Str0ng-pass!")
        self.other = User.objects.create_user(email="b@example.com", name="B", password="Str0ng-pass!")
        patient = {"date_of_birth": "1990-01-01", "gender": "female", "phone": "9999999999"}
        self.patient = Patient.objects.create(name="Mine", created_by=self.user, **patient)
        self.their_patient = Patient.objects.create(name="Theirs", created_by=self.other, **patient)
        self.doc1 = Doctor.objects.create(name="D1", specialization="ENT", email="d1@x.com", phone="9000000001", created_by=self.other)
        self.doc2 = Doctor.objects.create(name="D2", specialization="Ortho", email="d2@x.com", phone="9000000002", created_by=self.user)
        self.client.force_authenticate(self.user)

    def test_assign_list_get_by_patient_and_remove(self):
        res = self.client.post("/api/mappings/", {"patient": self.patient.id, "doctor": self.doc1.id})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["doctor_name"], "D1")
        mapping_id = res.data["id"]
        self.client.post("/api/mappings/", {"patient": self.patient.id, "doctor": self.doc2.id})

        self.assertEqual(self.client.get("/api/mappings/").data["count"], 2)

        res = self.client.get(f"/api/mappings/{self.patient.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual({d["name"] for d in res.data}, {"D1", "D2"})

        self.assertEqual(self.client.delete(f"/api/mappings/{mapping_id}/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual([d["name"] for d in self.client.get(f"/api/mappings/{self.patient.id}/").data], ["D2"])

    def test_duplicate_assignment_rejected(self):
        self.client.post("/api/mappings/", {"patient": self.patient.id, "doctor": self.doc1.id})
        res = self.client.post("/api/mappings/", {"patient": self.patient.id, "doctor": self.doc1.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_ids_rejected(self):
        res = self.client.post("/api/mappings/", {"patient": 999999, "doctor": 999999})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(res.data), {"patient", "doctor"})

    def test_other_users_patients_are_off_limits(self):
        res = self.client.post("/api/mappings/", {"patient": self.their_patient.id, "doctor": self.doc1.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        theirs = PatientDoctorMapping.objects.create(patient=self.their_patient, doctor=self.doc1)
        self.assertEqual(self.client.get("/api/mappings/").data["count"], 0)
        self.assertEqual(self.client.get(f"/api/mappings/{self.their_patient.id}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f"/api/mappings/{theirs.id}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(id=theirs.id).exists())
