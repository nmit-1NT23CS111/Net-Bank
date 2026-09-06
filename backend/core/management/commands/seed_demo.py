from decimal import Decimal
import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
from django.utils import timezone

from accounts.models import Account
from transactions.models import AuditLog, Transaction


class Command(BaseCommand):
    help = "Create idempotent demo data for the Net Bank local environment."

    def handle(self, *args, **options):
        User = get_user_model()
        admin_password = os.getenv("SEED_ADMIN_PASSWORD") or secrets.token_urlsafe(18)
        demo_password = os.getenv("SEED_DEMO_PASSWORD") or secrets.token_urlsafe(18)
        recipient_password = os.getenv("SEED_RECIPIENT_PASSWORD") or secrets.token_urlsafe(18)

        with db_transaction.atomic():
            admin = self._ensure_user(
                User,
                username="admin",
                email="admin@netbank.local",
                password=admin_password,
                first_name="Net",
                last_name="Admin",
                is_staff=True,
                is_superuser=True,
            )
            demo = self._ensure_user(
                User,
                username="demo",
                email="demo@netbank.local",
                password=demo_password,
                first_name="Demo",
                last_name="Customer",
                phone_number="+919999999999",
                city="Bengaluru",
                state="Karnataka",
                postal_code="560001",
            )
            recipient = self._ensure_user(
                User,
                username="recipient",
                email="recipient@netbank.local",
                password=recipient_password,
                first_name="Riya",
                last_name="Recipient",
                phone_number="+918888888888",
                city="Mumbai",
                state="Maharashtra",
                postal_code="400001",
            )

            primary = self._ensure_account(demo, "1000000001", "savings", "INR")
            checking = self._ensure_account(demo, "1000000002", "checking", "INR")
            recipient_account = self._ensure_account(recipient, "2000000001", "savings", "INR")

            if not Transaction.objects.filter(idempotency_key="seed-demo-deposit").exists():
                self._create_transaction(
                    from_account=primary,
                    to_account=primary,
                    transaction_type="deposit",
                    amount=Decimal("25000.0000"),
                    description="Opening deposit",
                    idempotency_key="seed-demo-deposit",
                )

            if not Transaction.objects.filter(idempotency_key="seed-demo-checking-deposit").exists():
                self._create_transaction(
                    from_account=checking,
                    to_account=checking,
                    transaction_type="deposit",
                    amount=Decimal("7500.0000"),
                    description="Checking account opening deposit",
                    idempotency_key="seed-demo-checking-deposit",
                )

            if not Transaction.objects.filter(idempotency_key="seed-demo-transfer").exists():
                self._create_transaction(
                    from_account=primary,
                    to_account=recipient_account,
                    transaction_type="transfer",
                    amount=Decimal("2750.0000"),
                    description="Demo transfer",
                    idempotency_key="seed-demo-transfer",
                )

            if not Transaction.objects.filter(idempotency_key="seed-demo-withdrawal").exists():
                self._create_transaction(
                    from_account=checking,
                    to_account=None,
                    transaction_type="withdrawal",
                    amount=Decimal("500.0000"),
                    description="ATM withdrawal demo",
                    idempotency_key="seed-demo-withdrawal",
                )

            self._ensure_audit_log(admin, "admin_action", "seed", "demo-data")

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"Customer login: demo@netbank.local / {demo_password}")
        self.stdout.write(f"Admin login: admin / {admin_password}")
        self.stdout.write("Recipient account for transfers: 2000000001")

    def _ensure_user(self, User, username, email, password, **defaults):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, **defaults},
        )
        changed = False

        if user.email != email:
            user.email = email
            changed = True

        for field, value in defaults.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed = True

        if created or not user.check_password(password):
            user.set_password(password)
            changed = True

        if changed:
            user.save()

        return user

    def _ensure_account(self, user, account_number, account_type, currency):
        account, _created = Account.objects.get_or_create(
            account_number=account_number,
            defaults={
                "user": user,
                "account_type": account_type,
                "currency": currency,
                "status": "active",
                "balance": Decimal("0.0000"),
            },
        )

        changed = False
        for field, value in {
            "user": user,
            "account_type": account_type,
            "currency": currency,
            "status": "active",
        }.items():
            if getattr(account, field) != value:
                setattr(account, field, value)
                changed = True

        if changed:
            account.save()

        return account

    def _create_transaction(
        self,
        from_account,
        to_account,
        transaction_type,
        amount,
        description,
        idempotency_key,
    ):
        if transaction_type in {"withdrawal", "transfer"}:
            from_account.balance -= amount
            from_account.save(update_fields=["balance"])

        if transaction_type in {"deposit", "transfer"} and to_account:
            to_account.balance += amount
            to_account.save(update_fields=["balance"])

        return Transaction.objects.create(
            from_account=from_account,
            to_account=to_account,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            status="completed",
            completed_at=timezone.now(),
            idempotency_key=idempotency_key,
            created_by_ip="127.0.0.1",
        )

    def _ensure_audit_log(self, user, action, resource_type, resource_id):
        AuditLog.objects.get_or_create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            defaults={
                "ip_address": "127.0.0.1",
                "user_agent": "seed_demo",
                "status": "success",
                "new_values": {"seeded": True},
            },
        )
