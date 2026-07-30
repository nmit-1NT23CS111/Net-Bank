# Net Bank - Quick Start Deployment Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- MySQL 5.7+
- Git

---

## Step 1: Backend Setup

### 1.1 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Configure Environment
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
```

**Critical environment variables to set:**
```
DJANGO_SECRET_KEY=generate-a-secure-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
FRONTEND_URL=http://localhost:5173  # or your production URL
```

### 1.3 Run Database Migrations
```bash
# Create migrations for new models
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

**New migrations will be created for:**
- `EmailVerificationToken`
- `OTPLogin`
- `OAuthProvider`
- `CustomUser.email_verified` field

### 1.4 Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 1.5 Test Backend
```bash
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000/api/v1/health/` to verify it's running.

---

## Step 2: Frontend Setup

### 2.1 Install Dependencies
```bash
cd frontend
npm install
```

### 2.2 Configure Environment
Create `.env` file:
```bash
cp .env.example .env
```

Update with your values:
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
```

### 2.3 Update Routes (if needed)
Add new routes to your router configuration. Example for React Router v6:

```typescript
// In your main router/App.tsx
import { VerifyEmailPage } from '@/pages/VerifyEmailPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { OTPLoginPage } from '@/pages/OTPLoginPage'
import { GoogleOAuthCallbackPage } from '@/pages/GoogleOAuthCallbackPage'

const routes = [
  {
    path: '/auth',
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      { path: 'verify-email', element: <VerifyEmailPage /> },
      { path: 'forgot-password', element: <ForgotPasswordPage /> },
      { path: 'reset-password', element: <ResetPasswordPage /> },
      { path: 'otp-login', element: <OTPLoginPage /> },
      { path: 'google/callback', element: <GoogleOAuthCallbackPage /> },
    ],
  },
  // ... rest of routes
]
```

### 2.4 Start Development Server
```bash
npm run dev
```

Visit `http://localhost:5173` to verify it's running.

---

## Step 3: Google OAuth Setup

### 3.1 Create Google OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Select "Web Application"
6. Add authorized redirect URIs:
   - `http://localhost:5173/auth/google/callback`
   - `https://yourdomain.com/auth/google/callback` (production)
7. Download credentials (Client ID + Secret)

### 3.2 Add to Backend `.env`
```
GOOGLE_OAUTH_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=xxxxx
```

### 3.3 Add to Frontend `.env`
```
VITE_GOOGLE_OAUTH_CLIENT_ID=xxxxx.apps.googleusercontent.com
```

---

## Step 4: Email Configuration

### 4.1 Gmail Setup (Recommended for Testing)

1. Enable 2-factor authentication on your Google account
2. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the generated password
3. Add to `.env`:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

### 4.2 Console Backend (For Testing Without SMTP)
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails will be printed to the console instead of being sent.

### 4.3 SendGrid (For Production)
1. Install: `pip install django-sendgrid-v5`
2. Add to settings: `EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'`
3. Add API key to `.env`:
   ```
   SENDGRID_API_KEY=your-sendgrid-api-key
   ```

---

## Step 5: Testing the Features

### Test 1: Email Verification
```bash
# 1. Register new account via frontend or:
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "1234567890"
  }'

# 2. Check console/email for verification link
# 3. Extract token and verify
curl -X POST http://localhost:8000/api/v1/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token": "token-from-email"}'
```

### Test 2: Password Reset
```bash
# Request reset
curl -X POST http://localhost:8000/api/v1/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Reset password with token
curl -X POST http://localhost:8000/api/v1/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "token-from-email",
    "new_password": "NewPass123!",
    "new_password2": "NewPass123!"
  }'
```

### Test 3: OTP Login
```bash
# Request OTP
curl -X POST http://localhost:8000/api/v1/auth/request-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "verified@example.com"}'

# Verify OTP (check console for code)
curl -X POST http://localhost:8000/api/v1/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email": "verified@example.com", "otp": "123456"}'
```

### Test 4: Google OAuth
1. Go to `http://localhost:5173/auth/login`
2. Click "Continue with Google"
3. Select your Google account
4. Should be redirected to dashboard with tokens

---

## Step 6: Run Full Application

### Terminal 1 - Backend
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Access the application
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/v1`
- Admin: `http://localhost:8000/admin` (if superuser created)

---

## Common Issues & Solutions

### Issue: Email not sending
**Solution:**
- Check EMAIL_BACKEND is not 'console' in production
- For Gmail: Verify App Password is correct
- Check SMTP settings: HOST, PORT, TLS
- Look for errors in console/logs

### Issue: Google OAuth not working
**Solution:**
- Verify GOOGLE_OAUTH_CLIENT_ID and SECRET
- Check redirect URI matches exactly in Google Console
- Clear browser cache/cookies
- Check CORS settings include frontend origin

### Issue: Database migration errors
**Solution:**
```bash
# Reset migrations (development only!)
python manage.py migrate accounts zero
python manage.py makemigrations
python manage.py migrate
```

### Issue: CORS errors
**Solution:**
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`
- Backend must restart after changing .env
- Check Access-Control-Allow-Origin header

---

## Production Checklist

- [ ] Change `DJANGO_DEBUG=false`
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure production email service
- [ ] Update `CORS_ALLOWED_ORIGINS` with production domain
- [ ] Update Google OAuth redirect URIs
- [ ] Set `FRONTEND_URL` to production domain
- [ ] Run `python manage.py collectstatic`
- [ ] Use production-grade database
- [ ] Set up logging and monitoring
- [ ] Configure rate limiting
- [ ] Enable CSRF protection
- [ ] Use secure session cookies

---

## Documentation

Detailed setup guide: `AUTHENTICATION_SETUP.md`

---

## Support

For issues:
1. Check error messages in console
2. Review `AUTHENTICATION_SETUP.md`
3. Check Django logs: `python manage.py runserver --debug`
4. Verify all environment variables are set
