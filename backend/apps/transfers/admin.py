from django.contrib import admin

from apps.transfers.models import TransferItem, TransferJob


class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 0
    readonly_fields = (
        "uuid",
        "sequence",
        "kind",
        "source_item_id",
        "source_path",
        "source_name",
        "dest_item_id",
        "dest_name",
        "status",
        "error_code",
        "error_message",
    )
    can_delete = False


@admin.register(TransferJob)
class TransferJobAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "operation",
        "status",
        "user",
        "source_item_name",
        "items_completed",
        "items_failed",
        "created_at",
    )
    list_filter = ("operation", "status")
    search_fields = ("uuid", "source_item_id", "source_item_name", "user__email")
    readonly_fields = ("uuid", "created_at", "updated_at", "celery_task_id")
    inlines = [TransferItemInline]
    ordering = ("-created_at",)


@admin.register(TransferItem)
class TransferItemAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "job",
        "sequence",
        "kind",
        "source_name",
        "status",
        "size_bytes",
    )
    list_filter = ("kind", "status")
    search_fields = ("source_item_id", "source_name", "dest_item_id")
    readonly_fields = ("uuid", "created_at", "updated_at")
