"""Email sending utilities for Net Bank"""
import os
from typing import Optional
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


class EmailService:
    """Service for sending transactional emails"""

    FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    SENDER_NAME = "Net Bank"

    @staticmethod
    def send_email(
        recipient_email: str,
        subject: str,
        template_name: str,
        context: dict,
        recipient_name: Optional[str] = None,
    ) -> bool:
        """
        Send email with HTML template support
        
        Args:
            recipient_email: Email address of recipient
            subject: Email subject
            template_name: Path to email template
            context: Template context variables
            recipient_name: Name of recipient (optional)
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            
            to_email = [recipient_email]
            if recipient_name:
                to_email = [f"{recipient_name} <{recipient_email}>"]
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=EmailService.FROM_EMAIL,
                recipient_list=to_email,
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")
            return False

    @staticmethod
    def send_verification_email(user, verification_token: str, frontend_url: str) -> bool:
        """Send email verification link"""
        verification_link = f"{frontend_url}/auth/verify-email?token={verification_token}"
        
        context = {
            "user_name": user.first_name or user.username,
            "verification_link": verification_link,
            "company_name": "Net Bank",
            "support_email": EmailService.FROM_EMAIL,
        }
        
        return EmailService.send_email(
            recipient_email=user.email,
            subject="Verify your Net Bank email address",
            template_name="accounts/emails/verification_email.html",
            context=context,
            recipient_name=user.first_name or user.username,
        )

    @staticmethod
    def send_password_reset_email(user, reset_token: str, frontend_url: str) -> bool:
        """Send password reset link"""
        reset_link = f"{frontend_url}/auth/reset-password?token={reset_token}"
        
        context = {
            "user_name": user.first_name or user.username,
            "reset_link": reset_link,
            "expiry_hours": 24,
            "company_name": "Net Bank",
            "support_email": EmailService.FROM_EMAIL,
        }
        
        return EmailService.send_email(
            recipient_email=user.email,
            subject="Reset your Net Bank password",
            template_name="accounts/emails/password_reset_email.html",
            context=context,
            recipient_name=user.first_name or user.username,
        )

    @staticmethod
    def send_otp_email(user, otp: str) -> bool:
        """Send OTP for login"""
        context = {
            "user_name": user.first_name or user.username,
            "otp": otp,
            "otp_expiry_minutes": 10,
            "company_name": "Net Bank",
            "support_email": EmailService.FROM_EMAIL,
        }
        
        return EmailService.send_email(
            recipient_email=user.email,
            subject="Your Net Bank login OTP",
            template_name="accounts/emails/otp_email.html",
            context=context,
            recipient_name=user.first_name or user.username,
        )

    @staticmethod
    def send_oauth_welcome_email(user) -> bool:
        """Send welcome email after OAuth signup"""
        context = {
            "user_name": user.first_name or user.username,
            "company_name": "Net Bank",
            "support_email": EmailService.FROM_EMAIL,
        }
        
        return EmailService.send_email(
            recipient_email=user.email,
            subject="Welcome to Net Bank",
            template_name="accounts/emails/oauth_welcome.html",
            context=context,
            recipient_name=user.first_name or user.username,
        )
