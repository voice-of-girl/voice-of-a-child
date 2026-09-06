from django.contrib import admin

from .models import Organisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation_type", "district", "country", "verification_status", "created_at")
    list_filter = ("organisation_type", "verification_status", "country")
    search_fields = ("name", "email", "district")