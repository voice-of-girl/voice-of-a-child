from django.contrib import admin

from .models import Challenge, Feedback, SupportRequest


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "organisation", "category", "priority", "status", "created_at")
    list_filter = ("status", "priority", "category", "organisation")
    search_fields = ("title", "description")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("category", "organisation", "status", "created_at")
    list_filter = ("status", "category", "organisation")


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("category", "organisation", "status", "created_at")
    list_filter = ("status", "category", "organisation")