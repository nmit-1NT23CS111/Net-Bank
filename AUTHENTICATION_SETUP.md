# Net Bank - Enhanced Authentication Setup Guide

This guide covers the new authentication features including Email Verification, Password Reset, OTP Login, and Google OAuth2.

## Table of Contents

1. [Email Verification](#email-verification)
2. [Password Reset](#password-reset)
3. [OTP Login](#otp-login)
4. [Google OAuth2](#google-oauth2)
5. [Environment Setup](#environment-setup)
6. [Database Setup](#database-setup)
7. [Testing](#testing)

---

## Email Verification

### Overview
New users must verify their email address before fully activating their account.

### Flow
1. User registers → Email verification token sent to inbox
2. User clicks verification link
3. Email marked as verified in database
4. User can now log in

### Implementation
- **Backend**: `VerifyEmailView`, `ResendVerificationEmailView`
- **Frontend**: `VerifyEmailPage`
- **Endpoints**:
  - `POST /api/v1/auth/verify-email/` - Verify email with token
  - `POST /api/v1/auth/resend-verification-email/` - Resend verification email

---

## Password Reset

### Overview
Users can reset forgotten passwords via secure email link.

### Flow
1. User clicks "Forgot Password"
2. Enters email address
3. Password reset link sent to email
4. User clicks link and sets new password
5. Tokens are marked as used to prevent replay attacks

### Implementation
- **Backend**: `ForgotPasswordView`, `ResetPasswordView`
- **Frontend**: `ForgotPasswordPage`, `ResetPasswordPage`
- **Endpoints**:
  - `POST /api/v1/auth/forgot-password/` - Request password reset
  - `POST /api/v1/auth/reset-password/` - Reset password with token

### Security Features
- Tokens expire after 24 hours
- One-time use only (marked as used after reset)
- Secure token generation using `secrets.token_urlsafe()`

---

## OTP Login

### Overview
Alternative login method using One-Time Passwords sent via email.

### Flow
1. User enters email address
2. 6-digit OTP sent to email (valid for 10 minutes)
3. User enters OTP
4. System verifies OTP with attempt limit
5. JWT tokens issued upon successful verification

### Implementation
- **Backend**: `RequestOTPView`, `VerifyOTPView`
- **Frontend**: `OTPLoginPage`
- **Endpoints**:
  - `POST /api/v1/auth/request-otp/` - Request OTP
  - `POST /api/v1/auth/verify-otp/` - Verify OTP and login

### Security Features
- 6-digit numeric OTP
- 10-minute expiration
- Maximum 5 attempts per OTP
- Rate limiting recommended

---

## Google OAuth2

### Overview
Users can sign up and log in using Google accounts.

### Flow
1. User clicks "Continue with Google"
2. Redirected to Google login
3. User grants permissions
4. OAuth callback received at backend
5. If new user: Account created automatically
6. JWT tokens issued
7. User redirected to dashboard

### Implementation
- **Backend**: `GoogleOAuthCallbackView`, `LinkedOAuthProvidersView`, `UnlinkOAuthProviderView`
- **Frontend**: `GoogleOAuthButton`, `GoogleOAuthCallbackPage`
- **Endpoints**:
  - `POST /api/v1/auth/google/callback/` - Handle OAuth callback
  - `GET /api/v1/auth/oauth/providers/` - List linked providers
  - `POST /api/v1/auth/oauth/unlink/` - Unlink OAuth provider

### Setup Steps

#### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Type: Web Application
   - Authorized redirect URIs:
     - `http://localhost:5173/auth/google/callback` (development)
     - `https://yourdomain.com/auth/google/callback` (production)
5. Note the Client ID and Client Secret

#### 2. Configure Backend

Add to `.env`:
```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

#### 3. Configure Frontend

Add to `.env`:
```
VITE_GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

#### 4. Test OAuth Flow

- Click "Continue with Google" on login page
- Select your Google account
- Should be redirected to dashboard with access tokens

### Security Features
- State parameter verification
- Token exchange at backend (never client-side)
- Email pre-verified for Google accounts
- Secure token storage

---

## Environment Setup

### Backend Requirements

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Create `.env` file** (see `.env.example`):
   ```
   DJANGO_DEBUG=true
   DJANGO_SECRET_KEY=your-secret-key
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   GOOGLE_OAUTH_CLIENT_ID=...
   GOOGLE_OAUTH_CLIENT_SECRET=...
   FRONTEND_URL=http://localhost:5173
   ```

3. **Email Configuration Options**:
   - **Gmail**: Use App Passwords (not regular password)
   - **SendGrid**: Install `django-sendgrid-v5` and configure
   - **Console**: For testing (prints emails to console)

### Frontend Requirements

1. **Create `.env` file**:
   ```
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_GOOGLE_OAUTH_CLIENT_ID=...
   ```

2. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

---

## Database Setup

### Run Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### New Models Created
- `EmailVerificationToken` - Email verification tokens
- `OTPLogin` - OTP login records
- `OAuthProvider` - OAuth provider accounts
- Updated `CustomUser` - Added `email_verified` field

---

## Testing

### Test Email Verification
1. Register new account
2. Check backend console for verification email
3. Copy verification token from email
4. Call `POST /api/v1/auth/verify-email/` with token
5. Verify `email_verified=true` in database

### Test Password Reset
1. Call `POST /api/v1/auth/forgot-password/` with email
2. Copy reset token from console
3. Call `POST /api/v1/auth/reset-password/` with token and new password
4. Log in with new password

### Test OTP Login
1. Email must be verified first
2. Call `POST /api/v1/auth/request-otp/` with email
3. Check console for OTP code
4. Call `POST /api/v1/auth/verify-otp/` with email and OTP
5. Should receive JWT tokens

### Test Google OAuth
1. Configure Google credentials in `.env`
2. Set `VITE_GOOGLE_OAUTH_CLIENT_ID` in frontend `.env`
3. Click "Continue with Google" on login page
4. Complete Google login flow
5. Should be redirected to dashboard

---

## Email Templates

All email templates are in `backend/accounts/templates/accounts/emails/`:

- `verification_email.html` - Email verification link
- `password_reset_email.html` - Password reset link
- `otp_email.html` - OTP code
- `oauth_welcome.html` - Welcome email for OAuth signup

Customize these templates with your branding!

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/verify-email/` | Verify email address |
| POST | `/auth/resend-verification-email/` | Resend verification email |
| POST | `/auth/forgot-password/` | Request password reset |
| POST | `/auth/reset-password/` | Reset password with token |
| POST | `/auth/request-otp/` | Request OTP for login |
| POST | `/auth/verify-otp/` | Verify OTP and login |
| POST | `/auth/google/callback/` | Handle Google OAuth callback |
| GET | `/auth/oauth/providers/` | List linked OAuth providers |
| POST | `/auth/oauth/unlink/` | Unlink OAuth provider |

---

## Troubleshooting

### Emails not being sent
- Check `EMAIL_BACKEND` setting
- For Gmail: Enable "Less secure app access" or use App Passwords
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- Try console backend first for testing: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`

### Google OAuth not working
- Verify `GOOGLE_OAUTH_CLIENT_ID` is correct
- Check redirect URI matches exactly
- Ensure frontend `.env` has correct client ID
- Check browser console for errors

### OTP not sending
- Verify email settings
- Check email address is verified first
- Test with console backend for debugging

---

## Security Recommendations

1. **Production Setup**:
   - Use strong `DJANGO_SECRET_KEY`
   - Enable HTTPS only
   - Set `DEBUG=false`
   - Use environment variables for secrets
   - Add rate limiting to auth endpoints

2. **Email Security**:
   - Use App Passwords instead of regular passwords
   - Consider using SendGrid or similar service
   - Implement email verification retry limits

3. **OAuth Security**:
   - Verify state parameter on callback
   - Use HTTPS for redirects
   - Regularly rotate OAuth credentials
   - Monitor for suspicious login patterns

---

## Support

For issues or questions, refer to:
- Django REST Framework docs: https://www.django-rest-framework.org/
- OAuth 2.0 Security: https://datatracker.ietf.org/doc/html/rfc6749
- Email Best Practices: https://docs.djangoproject.com/en/stable/topics/email/
