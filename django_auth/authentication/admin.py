from django.contrib import admin

from .apikey_models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):  # type: ignore
    list_display = (
        "owner",
        "name",
        "created_at",
        "expires_at",
        "revoked",
        "permission",
    )
    list_filter = ("owner", "revoked", "permission")
    search_fields = ("name", "owner__username")
    readonly_fields = ("key", "hashed_key", "created_at", "used")
    ordering = ("-created_at",)  # Default sorting by created_at in descending order
