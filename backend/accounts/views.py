from rest_framework import permissions, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import requests

from transactions.models import AuditLog

from .models import Account, LoginAttempt, EmailVerificationToken, OTPLogin, OAuthProvider, PasswordResetToken, CustomUser
from .serializers import (
    AccountBalanceSerializer,
    AccountCreateSerializer,
    AccountSerializer,
    ChangePasswordSerializer,
    CustomUserSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    UserRegisterSerializer,
    VerifyEmailSerializer,
    ResendVerificationEmailSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    OAuthCallbackSerializer,
    OAuthLoginSerializer,
    OAuthProviderSerializer,
)
from .emails import EmailService
from .utils import TokenGenerator


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class UserRegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        AuditLog.objects.create(
            user=user,
            action="register",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
            new_values={"username": user.username, "email": user.email},
        )

        return Response(
            {
                "success": True,
                "message": "Registration successful.",
                "user": CustomUserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payload = serializer.save()
        user = serializer.validated_data["user"]

        LoginAttempt.objects.create(
            user=user,
            email_or_username=request.data.get("username_or_email", ""),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            success=True,
        )
        AuditLog.objects.create(
            user=user,
            action="login",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
        )

        return Response({"success": True, **payload}, status=status.HTTP_200_OK)


class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {"success": True, "user": CustomUserSerializer(request.user).data},
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        AuditLog.objects.create(
            user=user,
            action="profile_update",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
            new_values={key: str(value) for key, value in serializer.validated_data.items()},
        )

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "user": CustomUserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        AuditLog.objects.create(
            user=request.user,
            action="password_change",
            resource_type="user",
            resource_id=str(request.user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
        )

        return Response(
            {"success": True, "message": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )


class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return AccountCreateSerializer
        if self.action == "balance":
            return AccountBalanceSerializer
        return AccountSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"success": True, "accounts": serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({"success": True, "account": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        account = serializer.save()

        AuditLog.objects.create(
            user=request.user,
            action="account_create",
            resource_type="account",
            resource_id=str(account.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
            new_values={
                "account_number": account.account_number,
                "account_type": account.account_type,
                "currency": account.currency,
            },
        )

        return Response(
            {
                "success": True,
                "message": "Bank account created successfully.",
                "account": AccountSerializer(account).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="balance")
    def balance(self, request, pk=None):
        serializer = AccountBalanceSerializer(self.get_object())
        return Response({"success": True, "balance": serializer.data}, status=status.HTTP_200_OK)


class VerifyEmailView(views.APIView):
    """Verify email with token"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_obj = EmailVerificationToken.objects.get(token=serializer.validated_data["token"])
        user = token_obj.user

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        token_obj.verified_at = timezone.now()
        token_obj.save(update_fields=["verified_at"])

        AuditLog.objects.create(
            user=user,
            action="email_verified",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
        )

        return Response(
            {"success": True, "message": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class ResendVerificationEmailView(views.APIView):
    """Resend email verification link"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(email=serializer.validated_data["email"])

        if user.email_verified:
            return Response(
                {"success": False, "message": "Email is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete existing token if any
        EmailVerificationToken.objects.filter(user=user).delete()

        # Create new token
        token = TokenGenerator.generate_email_verification_token()
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=TokenGenerator.get_token_expiry(hours=24),
        )

        frontend_url = request.data.get("frontend_url", settings.FRONTEND_URL)
        EmailService.send_verification_email(user, token, frontend_url)

        return Response(
            {"success": True, "message": "Verification email sent. Check your inbox."},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(views.APIView):
    """Request password reset link"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(email=serializer.validated_data["email"])

        # Delete existing reset tokens
        PasswordResetToken.objects.filter(user=user, used_at__isnull=True).delete()

        # Create new reset token
        token = TokenGenerator.generate_password_reset_token()
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=TokenGenerator.get_token_expiry(hours=24),
        )

        frontend_url = request.data.get("frontend_url", settings.FRONTEND_URL)
        EmailService.send_password_reset_email(user, token, frontend_url)

        return Response(
            {"success": True, "message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(views.APIView):
    """Reset password with token"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token_obj = PasswordResetToken.objects.get(token=serializer.validated_data["token"])
            if not token_obj.is_valid():
                return Response(
                    {"success": False, "message": "Token is invalid or expired."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = token_obj.user
            user.set_password(serializer.validated_data["new_password"])
            user.save(update_fields=["password"])

            token_obj.used_at = timezone.now()
            token_obj.save(update_fields=["used_at"])

            AuditLog.objects.create(
                user=user,
                action="password_reset",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=get_client_ip(request) or "127.0.0.1",
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                status="success",
            )

            return Response(
                {"success": True, "message": "Password reset successfully."},
                status=status.HTTP_200_OK,
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RequestOTPView(views.APIView):
    """Request OTP for login"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = CustomUser.objects.get(email=serializer.validated_data["email"])

        # Delete old OTPs for this user
        OTPLogin.objects.filter(user=user, is_verified=False).delete()

        # Generate OTP
        otp = TokenGenerator.generate_otp(length=6)
        OTPLogin.objects.create(
            user=user,
            email=user.email,
            otp=otp,
            expires_at=TokenGenerator.get_token_expiry(hours=0.17),  # 10 minutes
        )

        # Send OTP email
        EmailService.send_otp_email(user, otp)

        AuditLog.objects.create(
            user=user,
            action="otp_request",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
        )

        return Response(
            {"success": True, "message": "OTP sent to your email."},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(views.APIView):
    """Verify OTP and login"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp_obj = serializer.validated_data["otp_obj"]

        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.verified_at = timezone.now()
        otp_obj.save(update_fields=["is_verified", "verified_at"])

        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        LoginAttempt.objects.create(
            user=user,
            email_or_username=user.email,
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            success=True,
        )

        AuditLog.objects.create(
            user=user,
            action="login_otp",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=get_client_ip(request) or "127.0.0.1",
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            status="success",
        )

        return Response(
            {
                "success": True,
                "message": "OTP verified. You are now logged in.",
                "user": CustomUserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class GoogleOAuthCallbackView(views.APIView):
    """Handle Google OAuth callback"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OAuthCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        frontend_url = request.data.get("frontend_url", settings.FRONTEND_URL)

        try:
            # Exchange authorization code for access token
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{frontend_url}/auth/google/callback",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            # Get user info from Google
            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()

            # Check if OAuth provider exists
            oauth_provider = OAuthProvider.objects.filter(
                provider="google",
                provider_id=userinfo["id"],
            ).first()

            if oauth_provider:
                # Existing user
                user = oauth_provider.user
            else:
                # New user - create account
                username = userinfo["email"].split("@")[0]
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{userinfo['email'].split('@')[0]}{counter}"
                    counter += 1

                user = CustomUser.objects.create_user(
                    username=username,
                    email=userinfo["email"],
                    first_name=userinfo.get("given_name", ""),
                    last_name=userinfo.get("family_name", ""),
                    email_verified=True,  # Google emails are pre-verified
                    is_active=True,
                )

                # Create OAuth provider link
                OAuthProvider.objects.create(
                    user=user,
                    provider="google",
                    provider_id=userinfo["id"],
                    provider_email=userinfo["email"],
                    provider_username=userinfo.get("email", ""),
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token", ""),
                    expires_at=timezone.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                    profile_picture=userinfo.get("picture", ""),
                )

                # Send welcome email
                EmailService.send_oauth_welcome_email(user)

                AuditLog.objects.create(
                    user=user,
                    action="register_oauth",
                    resource_type="user",
                    resource_id=str(user.id),
                    ip_address=get_client_ip(request) or "127.0.0.1",
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                    status="success",
                    new_values={"username": user.username, "email": user.email, "provider": "google"},
                )

            # Generate JWT tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)

            LoginAttempt.objects.create(
                user=user,
                email_or_username=user.email,
                ip_address=get_client_ip(request) or "127.0.0.1",
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                success=True,
            )

            AuditLog.objects.create(
                user=user,
                action="login_oauth",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=get_client_ip(request) or "127.0.0.1",
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                status="success",
                new_values={"provider": "google"},
            )

            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "user": CustomUserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"success": False, "message": f"OAuth authentication failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LinkedOAuthProvidersView(views.APIView):
    """Get user's linked OAuth providers"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        providers = OAuthProvider.objects.filter(user=request.user)
        serializer = OAuthProviderSerializer(providers, many=True)
        return Response(
            {"success": True, "providers": serializer.data},
            status=status.HTTP_200_OK,
        )


class UnlinkOAuthProviderView(views.APIView):
    """Unlink OAuth provider from account"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        provider = request.data.get("provider")

        try:
            oauth = OAuthProvider.objects.get(user=request.user, provider=provider)
            oauth.delete()

            AuditLog.objects.create(
                user=request.user,
                action="unlink_oauth",
                resource_type="user",
                resource_id=str(request.user.id),
                ip_address=get_client_ip(request) or "127.0.0.1",
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                status="success",
                new_values={"provider": provider},
            )

            return Response(
                {"success": True, "message": f"{provider} account unlinked successfully."},
                status=status.HTTP_200_OK,
            )
        except OAuthProvider.DoesNotExist:
            return Response(
                {"success": False, "message": "OAuth provider not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
