from django.contrib import admin

from .models import UssdSession


@admin.register(UssdSession)
class UssdSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'phone_number', 'state', 'completed', 'expires_at', 'updated_at')
    list_filter = ('state', 'completed')
    search_fields = ('session_id', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
