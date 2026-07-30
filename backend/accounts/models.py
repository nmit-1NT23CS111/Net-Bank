import random
import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    kyc_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    def is_kyc_verified(self):
        return self.kyc_verified_at is not None


class Account(models.Model):
    ACCOUNT_TYPES = (
        ("savings", "Savings Account"),
        ("checking", "Checking Account"),
        ("credit", "Credit Account"),
    )
    ACCOUNT_STATUS = (
        ("active", "Active"),
        ("frozen", "Frozen"),
        ("closed", "Closed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="accounts")
    account_number = models.CharField(max_length=20, unique=True, db_index=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default="savings")
    balance = models.DecimalField(
        decimal_places=4,
        max_digits=19,
        default=Decimal("0.0000"),
        validators=[MinValueValidator(Decimal("0.0000"))],
    )
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default="active", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accounts"
        ordering = ["-created_at"]
        unique_together = ("user", "account_number")
        indexes = [
            models.Index(fields=["user", "account_number"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.account_number} ({self.user.username})"

    @staticmethod
    def generate_account_number():
        while True:
            account_number = str(random.randint(10**9, 10**10 - 1))
            if not Account.objects.filter(account_number=account_number).exists():
                return account_number

    def can_withdraw(self, amount):
        from django.conf import settings

        return self.balance - amount >= Decimal(str(settings.MINIMUM_ACCOUNT_BALANCE))

    def close_account(self):
        self.status = "closed"
        self.closed_at = timezone.now()
        self.save(update_fields=["status", "closed_at"])


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_reset_tokens"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Reset token for {self.user.email}"

    def is_valid(self):
        return self.used_at is None and timezone.now() < self.expires_at


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="email_verification_token")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_verification_tokens"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Verification token for {self.user.email}"

    def is_valid(self):
        return self.verified_at is None and timezone.now() < self.expires_at


class LoginAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="login_attempts",
        null=True,
        blank=True,
    )
    email_or_username = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "login_attempts"
        indexes = [
            models.Index(fields=["ip_address", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login attempt: {self.email_or_username} from {self.ip_address}"


class OTPLogin(models.Model):
    """OTP-based login verification"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="otp_logins")
    email = models.EmailField()
    otp = models.CharField(max_length=6, db_index=True)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_logins"
        indexes = [
            models.Index(fields=["email", "otp"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"OTP for {self.email}"

    def is_valid(self):
        return (
            not self.is_verified
            and self.attempts < self.max_attempts
            and timezone.now() < self.expires_at
        )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=["attempts"])


class OAuthProvider(models.Model):
    """Social OAuth provider accounts linked to users"""
    PROVIDER_CHOICES = (
        ("google", "Google"),
        ("github", "GitHub"),
        ("microsoft", "Microsoft"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="oauth_providers")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, db_index=True)
    provider_id = models.CharField(max_length=500)
    provider_email = models.EmailField()
    provider_username = models.CharField(max_length=255, blank=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    profile_picture = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "oauth_providers"
        unique_together = ("provider", "provider_id")
        indexes = [
            models.Index(fields=["provider", "provider_id"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_provider_display()}"
