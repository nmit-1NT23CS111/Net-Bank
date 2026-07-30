from django.contrib import admin

from .models import AuditLog, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "transaction_type",
        "from_account",
        "to_account",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("transaction_type", "status")
    search_fields = ("reference_number", "description", "from_account__account_number", "to_account__account_number")
    readonly_fields = ("id", "reference_number", "created_at", "completed_at")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "resource_type", "resource_id", "status", "created_at")
    list_filter = ("action", "status", "resource_type")
    search_fields = ("resource_id", "user__email", "user__username", "ip_address")
    readonly_fields = ("id", "created_at")
