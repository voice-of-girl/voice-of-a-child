from django.contrib import admin

from apps.programmes.models import Programme, ProgrammeEnrollment, ProgrammeKPI, ProgrammeObjective


class ObjectiveInline(admin.TabularInline):
    model = ProgrammeObjective
    extra = 0


class KPIInline(admin.TabularInline):
    model = ProgrammeKPI
    extra = 0


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("title", "organisation", "category", "status", "start_date", "end_date")
    list_filter = ("status", "category")
    search_fields = ("title", "organisation__name")
    inlines = [ObjectiveInline, KPIInline]


@admin.register(ProgrammeEnrollment)
class ProgrammeEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("programme", "participant", "status", "progress", "enrolled_at")
    list_filter = ("status",)
