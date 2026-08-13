from django.contrib import admin

from apps.activity.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "action",
        "resource_type",
        "resource_name",
        "status",
        "user",
        "provider",
        "created_at",
    )
    list_filter = ("action", "resource_type", "status", "provider")
    search_fields = ("uuid", "resource_id", "resource_name", "user__email", "request_id")
    readonly_fields = ("uuid", "created_at", "updated_at", "metadata")
    ordering = ("-created_at",)
