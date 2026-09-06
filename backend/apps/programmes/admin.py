from django.contrib import admin

from .models import Programme


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "status", "start_date", "end_date")
    list_filter = ("status", "organisation")
    search_fields = ("name", "organisation__name")