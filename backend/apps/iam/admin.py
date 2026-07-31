from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, EmailVerificationToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        "email",
        "username",
        "is_verified",
        "is_staff",
        "created_at",
    )

    ordering = ("created_at",)

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "display_name",
                    "profile_picture",
                    "bio",
                    "timezone",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Verification", {"fields": ("is_verified",)}),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "token",
        "expires_at",
        "verified_at",
        "created_at",
    )

    readonly_fields = (
        "token",
        "created_at",
        "verified_at",
    )
