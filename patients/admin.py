from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "gender", "date_of_birth", "phone", "created_by", "created_at")
    list_filter = ("gender",)
    search_fields = ("name", "phone", "email")
