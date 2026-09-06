from django.contrib import admin

from apps.organisations.models import Organisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation_type", "email", "district", "status")
    list_filter = ("organisation_type", "status", "country")
    search_fields = ("name", "email", "contact_person")
