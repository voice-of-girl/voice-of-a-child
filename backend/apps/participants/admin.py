from django.contrib import admin

from apps.participants.models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "district", "education_level", "verification_status", "organisation")
    list_filter = ("verification_status", "education_level", "employment_status", "gender")
    search_fields = ("full_name", "phone_number", "email", "district")
