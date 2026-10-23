from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from patients.models import Patient

User = get_user_model()


def error_fields(res):
    """Field names in a VALIDATION_ERROR response."""
    return {d["field"] for d in res.data["error"]["details"]}


class HealthTests(APITestCase):
    def test_health_is_public_and_reports_db(self):
        res = self.client.get("/health/", HTTP_X_REQUEST_ID="abc123")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, {"status": "ok", "database": "up"})
        self.assertEqual(res["X-Request-Id"], "abc123")


class ErrorAndPaginationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="a@example.com", name="A", password="Str0ng-pass!")
        self.client.force_authenticate(self.user)

    def test_errors_share_one_shape(self):
        self.client.force_authenticate(None)
        res = self.client.get("/api/patients/")
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.data["error"]["code"], "UNAUTHORIZED")
        self.assertIn("message", res.data["error"])

    @override_settings(DEBUG=False)
    def test_unknown_route_is_json_404(self):
        res = self.client.get("/nope/")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["error"]["code"], "NOT_FOUND")

    def test_unknown_fields_rejected(self):
        res = self.client.post(
            "/api/doctors/", {"name": "D", "specialization": "ENT", "email": "d@x.com", "phone": "9000000001", "phnoe": "1"}
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(res.data["error"]["details"], [{"field": "phnoe", "message": "Unknown field."}])

    def test_oversized_json_body_rejected(self):
        res = self.client.post("/api/patients/", {"name": "x" * 200_000}, format="json")
        self.assertEqual(res.status_code, 413)
        self.assertEqual(res.json()["error"]["code"], "PAYLOAD_TOO_LARGE")

    def test_pagination_page_and_limit(self):
        Patient.objects.bulk_create(
            Patient(name=f"P{i}", date_of_birth="1990-01-01", gender="male", phone="9999999999", created_by=self.user)
            for i in range(5)
        )
        res = self.client.get("/api/patients/?page=2&limit=2")
        self.assertEqual(res.data["meta"], {"page": 2, "limit": 2, "total": 5, "total_pages": 3})
        self.assertEqual(len(res.data["data"]), 2)
        self.assertEqual(self.client.get("/api/patients/?limit=500").data["meta"]["limit"], 100)
