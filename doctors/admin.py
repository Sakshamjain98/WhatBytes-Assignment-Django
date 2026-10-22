from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "email", "experience_years", "created_by")
    list_filter = ("specialization",)
    search_fields = ("name", "email", "specialization")
