from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "organisation", "report_type", "file_format", "status", "created_at")
    list_filter = ("status", "report_type", "file_format", "organisation")
    search_fields = ("title",)