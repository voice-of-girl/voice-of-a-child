from django.contrib import admin

from apps.monitoring.models import Challenge


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("description", "category", "status", "programme", "participant", "date_reported")
    list_filter = ("category", "status")
    search_fields = ("description",)
