from django.contrib import admin

from .models import ImpactMeasurement, ImpactProject, KPI


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "programme", "baseline", "current_value", "target")
    list_filter = ("organisation", "programme")


@admin.register(ImpactProject)
class ImpactProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation", "status", "start_date", "end_date")
    list_filter = ("status", "organisation")


@admin.register(ImpactMeasurement)
class ImpactMeasurementAdmin(admin.ModelAdmin):
    list_display = ("metric", "organisation", "value", "period")