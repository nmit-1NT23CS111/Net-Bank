"""Utility functions for authentication"""
import secrets
import string
import uuid
from datetime import timedelta

import pyotp
from django.conf import settings
from django.utils import timezone


class TokenGenerator:
    """Generate secure tokens for various authentication flows"""

    @staticmethod
    def generate_email_verification_token() -> str:
        """Generate token for email verification"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate token for password reset"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate OTP (One-Time Password)"""
        digits = string.digits
        return "".join(secrets.choice(digits) for _ in range(length))

    @staticmethod
    def get_token_expiry(hours: int = 24) -> timezone.datetime:
        """Get token expiry time"""
        return timezone.now() + timedelta(hours=hours)


class OTPGenerator:
    """Generate and verify TOTP for 2FA"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a base32 encoded secret for TOTP"""
        return pyotp.random_base32()

    @staticmethod
    def get_totp(secret: str) -> pyotp.TOTP:
        """Get TOTP instance from secret"""
        return pyotp.TOTP(secret)

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

    @staticmethod
    def get_provisioning_uri(secret: str, name: str, issuer: str = "Net Bank") -> str:
        """Get provisioning URI for QR code generation"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=name, issuer_name=issuer)
