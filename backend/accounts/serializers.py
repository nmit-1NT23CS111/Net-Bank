from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Account, CustomUser, EmailVerificationToken, OTPLogin, OAuthProvider
from .utils import TokenGenerator


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "address",
            "city",
            "state",
            "postal_code",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "username", "email", "created_at", "updated_at")


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone_number",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        if CustomUser.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username is already taken."})
        if CustomUser.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs["username_or_email"]
        password = attrs["password"]

        if "@" in username_or_email:
            try:
                username_or_email = CustomUser.objects.get(email=username_or_email).username
            except CustomUser.DoesNotExist as exc:
                raise serializers.ValidationError({"detail": "Invalid credentials."}) from exc

        user = authenticate(
            request=self.context.get("request"),
            username=username_or_email,
            password=password,
        )
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return {
            "user": CustomUserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "address",
            "city",
            "state",
            "postal_code",
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context["request"]
        if not request.user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Current password is incorrect."})
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class AccountSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "account_number",
            "account_type",
            "balance",
            "currency",
            "status",
            "created_at",
            "closed_at",
            "owner_name",
        )
        read_only_fields = fields

    def get_owner_name(self, obj):
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return full_name or obj.user.username


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("account_type", "currency")

    def validate_currency(self, value):
        return value.upper()

    def create(self, validated_data):
        return Account.objects.create(
            user=self.context["request"].user,
            account_number=Account.generate_account_number(),
            **validated_data,
        )


class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "account_number", "balance", "currency", "status")
        read_only_fields = fields


class VerifyEmailSerializer(serializers.Serializer):
    """Verify email with token"""
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            token_obj = EmailVerificationToken.objects.get(token=value)
            if not token_obj.is_valid():
                raise serializers.ValidationError("Token is invalid or expired.")
            return value
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Token is invalid or expired.")


class ResendVerificationEmailSerializer(serializers.Serializer):
    """Resend email verification link"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email not found.")
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """Request password reset link"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email not found.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password with token"""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})
        return attrs


class RequestOTPSerializer(serializers.Serializer):
    """Request OTP for login"""
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
            if not user.email_verified:
                raise serializers.ValidationError("Email is not verified.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email not found.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP for login"""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs["email"]
        otp = attrs["otp"]

        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = OTPLogin.objects.filter(user=user, email=email).order_by("-created_at").first()

            if not otp_obj:
                raise serializers.ValidationError({"otp": "No OTP found for this email."})

            if not otp_obj.is_valid():
                raise serializers.ValidationError({"otp": "OTP has expired or max attempts reached."})

            if otp_obj.otp != otp:
                otp_obj.increment_attempts()
                raise serializers.ValidationError({"otp": "Invalid OTP."})

            attrs["user"] = user
            attrs["otp_obj"] = otp_obj
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        return attrs


class OAuthCallbackSerializer(serializers.Serializer):
    """Handle OAuth provider callback"""
    provider = serializers.CharField(max_length=20, required=False, allow_blank=True)
    code = serializers.CharField()
    state = serializers.CharField(required=False, allow_blank=True)


class OAuthLoginSerializer(serializers.Serializer):
    """OAuth token login"""
    provider = serializers.CharField(max_length=20)
    access_token = serializers.CharField()


class OAuthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthProvider
        fields = ("id", "provider", "provider_email", "provider_username", "profile_picture", "created_at")
        read_only_fields = fields


class LinkedOAuthSerializer(serializers.Serializer):
    """List user's linked OAuth providers"""
    providers = OAuthProviderSerializer(many=True, read_only=True)
