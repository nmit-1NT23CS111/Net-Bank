from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account, CustomUser, EmailVerificationToken, LoginAttempt, PasswordResetToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "created_at")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)
    fieldsets = UserAdmin.fieldsets + (
        (
            "Banking Profile",
            {
                "fields": (
                    "phone_number",
                    "date_of_birth",
                    "address",
                    "city",
                    "state",
                    "postal_code",
                    "kyc_verified_at",
                )
            },
        ),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "user", "account_type", "balance", "currency", "status", "created_at")
    list_filter = ("account_type", "status", "currency")
    search_fields = ("account_number", "user__username", "user__email")
    readonly_fields = ("id", "created_at", "closed_at")


admin.site.register(PasswordResetToken)
admin.site.register(EmailVerificationToken)
admin.site.register(LoginAttempt)
