from config.exceptions import Conflict

from .models import PatientDoctorMapping


def assign_doctor(patient, doctor, notes=""):
    """Assign `doctor` to `patient`; 409 if already assigned (the unique constraint also catches races)."""
    if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
        raise Conflict("This doctor is already assigned to this patient.")
    return PatientDoctorMapping.objects.create(patient=patient, doctor=doctor, notes=notes)
