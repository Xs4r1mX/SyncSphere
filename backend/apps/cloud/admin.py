from django.contrib import admin

from apps.cloud.models import CloudConnection, OAuthState


@admin.register(CloudConnection)
class CloudConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "provider",
        "account_email",
        "status",
        "user",
        "created_at",
    )
    list_filter = ("provider", "status")
    search_fields = (
        "display_name",
        "account_email",
        "provider_account_id",
        "user__email",
    )
    readonly_fields = (
        "uuid",
        "credentials_encrypted",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(OAuthState)
class OAuthStateAdmin(admin.ModelAdmin):
    list_display = (
        "provider",
        "user",
        "state",
        "expires_at",
        "consumed_at",
        "created_at",
    )
    list_filter = ("provider",)
    search_fields = ("state", "user__email")
    readonly_fields = (
        "uuid",
        "state",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
