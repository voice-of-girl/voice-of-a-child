from django.contrib import admin

from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "programme", "organisation", "status")
    list_filter = ("status", "organisation", "programme")
    search_fields = ("name", "email", "external_reference")