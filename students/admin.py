from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "username", "first_name", "last_name", "role", "is_active", "is_staff", "verified"]
    search_fields = ["email", "username", "first_name", "last_name"]
    list_filter = ["role", "is_active", "is_staff", "verified"]

    # Campos solo lectura (ej: last_login)
    readonly_fields = ("last_login",)

    # Formulario de edición (change_view)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {
            "fields": (
                "username", "first_name", "last_name",
                "birthday", "aura", "specialty", "profile_picture"
            )
        }),
        ("Teacher Info", {"fields": ("experience_years", "verified", "hourly_rate")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),  # joined_at eliminado
    )

    # Formulario para crear usuarios (add_view)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "username", "first_name", "last_name", "role",
                "birthday", "aura", "specialty", "profile_picture",
                "experience_years", "verified", "hourly_rate",
                "password1", "password2"
            ),
        }),
    )
