import uuid
from datetime import timedelta

from django.conf import settings
from django.db import transaction as db_transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from accounts.models import Account

from .models import AuditLog, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    from_account_number = serializers.CharField(source="from_account.account_number", read_only=True)
    to_account_number = serializers.CharField(source="to_account.account_number", read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "from_account",
            "from_account_number",
            "to_account",
            "to_account_number",
            "transaction_type",
            "amount",
            "description",
            "status",
            "reference_number",
            "created_at",
            "completed_at",
            "idempotency_key",
        )
        read_only_fields = fields


class AccountScopedTransactionSerializer(serializers.Serializer):
    account_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=19, decimal_places=4, min_value=0.0001)
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def get_account(self, value):
        try:
            account = Account.objects.get(id=value, user=self.context["request"].user)
        except Account.DoesNotExist as exc:
            raise serializers.ValidationError("Account not found.") from exc

        if account.status != "active":
            raise serializers.ValidationError("Account is not active.")
        return account

    def validate_account_id(self, value):
        self.account = self.get_account(value)
        return value


class DepositSerializer(AccountScopedTransactionSerializer):
    def create(self, validated_data):
        with db_transaction.atomic():
            account = Account.objects.select_for_update().get(id=self.account.id)
            txn = Transaction.objects.create(
                from_account=account,
                to_account=account,
                transaction_type="deposit",
                amount=validated_data["amount"],
                description=validated_data.get("description", ""),
                status="pending",
                idempotency_key=str(uuid.uuid4()),
                created_by_ip=self.context.get("client_ip"),
            )
            Account.objects.filter(id=account.id).update(balance=F("balance") + txn.amount)
            account.refresh_from_db()
            txn.status = "completed"
            txn.completed_at = timezone.now()
            txn.save(update_fields=["status", "completed_at"])
            txn.from_account = account
            txn.to_account = account
            return txn


class WithdrawalSerializer(AccountScopedTransactionSerializer):
    def validate(self, attrs):
        account = getattr(self, "account", None) or self.get_account(attrs["account_id"])
        if not account.can_withdraw(attrs["amount"]):
            raise serializers.ValidationError(
                {
                    "amount": (
                        f"Insufficient funds. Minimum remaining balance is "
                        f"{settings.MINIMUM_ACCOUNT_BALANCE}."
                    )
                }
            )
        return attrs

    def create(self, validated_data):
        with db_transaction.atomic():
            account = Account.objects.select_for_update().get(id=self.account.id)
            if not account.can_withdraw(validated_data["amount"]):
                raise serializers.ValidationError({"amount": "Insufficient funds."})

            txn = Transaction.objects.create(
                from_account=account,
                transaction_type="withdrawal",
                amount=validated_data["amount"],
                description=validated_data.get("description", ""),
                status="pending",
                idempotency_key=str(uuid.uuid4()),
                created_by_ip=self.context.get("client_ip"),
            )
            Account.objects.filter(id=account.id).update(balance=F("balance") - txn.amount)
            account.refresh_from_db()
            txn.status = "completed"
            txn.completed_at = timezone.now()
            txn.save(update_fields=["status", "completed_at"])
            txn.from_account = account
            return txn


class TransferSerializer(serializers.Serializer):
    from_account_id = serializers.UUIDField()
    to_account_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=19, decimal_places=4, min_value=0.0001)
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate(self, attrs):
        request_user = self.context["request"].user
        try:
            from_account = Account.objects.get(id=attrs["from_account_id"], user=request_user)
        except Account.DoesNotExist as exc:
            raise serializers.ValidationError({"from_account_id": "Source account not found."}) from exc

        try:
            to_account = Account.objects.get(account_number=attrs["to_account_number"])
        except Account.DoesNotExist as exc:
            raise serializers.ValidationError({"to_account_number": "Destination account not found."}) from exc

        if from_account.status != "active":
            raise serializers.ValidationError({"from_account_id": "Source account is not active."})
        if to_account.status != "active":
            raise serializers.ValidationError({"to_account_number": "Destination account is not active."})
        if from_account.id == to_account.id:
            raise serializers.ValidationError({"to_account_number": "Choose a different destination account."})
        if not from_account.can_withdraw(attrs["amount"]):
            raise serializers.ValidationError({"amount": "Insufficient funds for this transfer."})

        recent_transfers = Transaction.objects.filter(
            from_account=from_account,
            transaction_type="transfer",
            created_at__gte=timezone.now() - timedelta(hours=1),
        ).count()
        if recent_transfers >= settings.MAX_TRANSFERS_PER_HOUR:
            raise serializers.ValidationError(
                {"detail": f"Transfer limit exceeded. Max {settings.MAX_TRANSFERS_PER_HOUR} per hour."}
            )

        attrs["from_account"] = from_account
        attrs["to_account"] = to_account
        return attrs

    def create(self, validated_data):
        idempotency_key = validated_data.get("idempotency_key") or str(uuid.uuid4())
        existing = Transaction.objects.filter(
            idempotency_key=idempotency_key,
            transaction_type="transfer",
        ).first()
        if existing:
            return existing

        with db_transaction.atomic():
            first_id, second_id = sorted(
                [validated_data["from_account"].id, validated_data["to_account"].id],
                key=str,
            )
            locked_accounts = {
                account.id: account
                for account in Account.objects.select_for_update().filter(id__in=[first_id, second_id])
            }
            from_account = locked_accounts[validated_data["from_account"].id]
            to_account = locked_accounts[validated_data["to_account"].id]

            if not from_account.can_withdraw(validated_data["amount"]):
                raise serializers.ValidationError({"amount": "Insufficient funds for this transfer."})

            transfer = Transaction.objects.create(
                from_account=from_account,
                to_account=to_account,
                transaction_type="transfer",
                amount=validated_data["amount"],
                description=validated_data.get("description", ""),
                status="pending",
                idempotency_key=idempotency_key,
                created_by_ip=self.context.get("client_ip"),
            )
            Account.objects.filter(id=from_account.id).update(balance=F("balance") - transfer.amount)
            Account.objects.filter(id=to_account.id).update(balance=F("balance") + transfer.amount)
            from_account.refresh_from_db()
            to_account.refresh_from_db()
            transfer.status = "completed"
            transfer.completed_at = timezone.now()
            transfer.save(update_fields=["status", "completed_at"])
            transfer.from_account = from_account
            transfer.to_account = to_account
            return transfer


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user",
            "user_email",
            "action",
            "resource_type",
            "resource_id",
            "old_values",
            "new_values",
            "ip_address",
            "status",
            "error_message",
            "created_at",
        )
        read_only_fields = fields
