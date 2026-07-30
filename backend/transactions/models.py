import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import Account, CustomUser


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
        ("fee", "Fee"),
    )
    TRANSACTION_STATUS = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("reversed", "Reversed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="outgoing_transactions",
        db_index=True,
    )
    to_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="incoming_transactions",
        null=True,
        blank=True,
        db_index=True,
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, db_index=True)
    amount = models.DecimalField(
        decimal_places=4,
        max_digits=19,
        validators=[MinValueValidator(Decimal("0.0001"))],
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default="pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    reference_number = models.CharField(max_length=255, unique=True, db_index=True)
    created_by_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["from_account", "-created_at"]),
            models.Index(fields=["to_account", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["transaction_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.transaction_type}: {self.amount} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    ACTION_TYPES = (
        ("login", "User Login"),
        ("logout", "User Logout"),
        ("login_failed", "Failed Login Attempt"),
        ("register", "User Registration"),
        ("profile_update", "Profile Update"),
        ("password_change", "Password Change"),
        ("password_reset", "Password Reset"),
        ("account_create", "Account Created"),
        ("account_close", "Account Closed"),
        ("account_freeze", "Account Frozen"),
        ("account_unfreeze", "Account Unfrozen"),
        ("transaction_initiated", "Transaction Initiated"),
        ("transaction_completed", "Transaction Completed"),
        ("transaction_failed", "Transaction Failed"),
        ("transaction_reversed", "Transaction Reversed"),
        ("admin_action", "Admin Action"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
        null=True,
        blank=True,
        db_index=True,
    )
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    resource_type = models.CharField(max_length=50, db_index=True)
    resource_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="success")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
            models.Index(fields=["ip_address", "-created_at"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self):
        resource_info = f" (Resource: {self.resource_id})" if self.resource_id else ""
        return f"{self.get_action_display()}{resource_info} - {self.user}"
