# 🚀 Complete Project Setup & Troubleshooting Guide

## ✅ Backend Status
✓ Running on port 8000
✓ Migrations applied
✓ System checks passed

---

## ❌ Issues Found & Solutions

### Issue 1: Email Features Not Working (OTP, Forgot Password)
**Problem**: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are placeholders
**Solution**: Configure Gmail SMTP credentials

#### Step 1: Get Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Google generates 16-character password
4. Copy it

#### Step 2: Update `.env` in `backend/`
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=paste-16-char-app-password-here
```

**For Testing WITHOUT Email Setup:**
Temporarily use console backend in `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
(Emails will print to console instead of sending)

---

### Issue 2: OAuth Error - "OAuth client was not found" (401: invalid_client)
**Problem**: GOOGLE_OAUTH_CLIENT_ID and SECRET are placeholders

#### Step 1: Create Google OAuth Credentials
1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable "Google+ API"
4. Go to Credentials → Create OAuth 2.0 Credentials
5. Choose "Web Application"
6. Add Authorized Redirect URIs:
   ```
   http://localhost:5173/auth/google/callback
   https://your-domain.com/auth/google/callback  (production)
   ```
7. Copy Client ID and Client Secret

#### Step 2: Update Backend `.env`
```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

#### Step 3: Update Frontend `.env`
Create file: `frontend/.env`
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

---

## 🏃 How to Run Full Project

### Terminal 1: Backend
```powershell
cd "d:\programme files\net-bank\backend"
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

Wait for:
```
Starting development server at http://127.0.0.1:8000/
```

### Terminal 2: Frontend
```powershell
cd "d:\programme files\net-bank\frontend"
npm install  # Only first time
npm run dev
```

Wait for:
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### Terminal 3 (Optional): Watch Logs
```powershell
cd "d:\programme files\net-bank\backend"
tail -f logs/debug.log  # If you set up logging
```

---

## 🧪 Testing Each Feature

### Test 1: Register & Email Verification
1. Go to http://localhost:5173/auth/register
2. Fill form and submit
3. **If console backend**: Check backend terminal for verification link
4. **If Gmail**: Check email inbox
5. Copy token and verify

### Test 2: OTP Login
1. Go to http://localhost:5173/auth/otp-login
2. Enter verified email
3. Check backend console for 6-digit OTP
4. Enter OTP
5. Should see dashboard

### Test 3: Forgot Password
1. Go to http://localhost:5173/auth/forgot-password
2. Enter email
3. Check console/email for reset link
4. Click link and reset password

### Test 4: Google OAuth
1. Go to http://localhost:5173/auth/login
2. Click "Continue with Google"
3. Select account
4. Should redirect to dashboard

---

## 📋 Complete .env Configuration

### Backend (d:\programme files\net-bank\backend\.env)
```
# Django
DJANGO_SECRET_KEY=django-insecure-net-bank-local-dev-key
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
MYSQL_DATABASE=net_bank
MYSQL_USER=root
MYSQL_PASSWORD=Mysql@123
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306

# Email (REQUIRED for OTP, Password Reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# Google OAuth (REQUIRED for "Continue with Google")
GOOGLE_OAUTH_CLIENT_ID=YOUR-CLIENT-ID.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=YOUR-CLIENT-SECRET

# Frontend & CORS
FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Optional
MAX_TRANSFERS_PER_HOUR=10
```

### Frontend (d:\programme files\net-bank\frontend\.env)
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_GOOGLE_OAUTH_CLIENT_ID=YOUR-CLIENT-ID.apps.googleusercontent.com
```

---

## 🔧 Quick Fixes Checklist

- [ ] Backend running on 8000?
- [ ] Frontend running on 5173?
- [ ] Backend `.env` has real email credentials?
- [ ] Backend `.env` has real Google OAuth credentials?
- [ ] Frontend `.env` exists with Google Client ID?
- [ ] Migrations applied? (`python manage.py migrate`)
- [ ] MySQL running and database exists?

---

## ⚡ Development Tips

### Clear Local Storage (if login stuck)
Browser console:
```javascript
localStorage.clear()
location.reload()
```

### Reset Database (CAUTION - DELETES ALL DATA)
```powershell
# Drop database
mysql -u root -p -e "DROP DATABASE net_bank; CREATE DATABASE net_bank;"

# Re-migrate
python manage.py migrate
```

### Check Email Configuration
```powershell
python manage.py shell
>>> from accounts.emails import EmailService
>>> EmailService.send_email(
...     'test@example.com',
...     'Test',
...     'verification_email.html',
...     {'verification_link': 'test'}
... )
```

### View Active Tokens
```powershell
python manage.py shell
>>> from rest_framework_simplejwt.tokens import Token
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.first()
>>> Token.for_user(user)
```

---

## 🐛 Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Email not verified" on OTP | Email in `.env` is placeholder | Configure real Gmail credentials |
| 401 invalid_client OAuth | Google Client ID is placeholder | Get real Client ID from Google Console |
| Frontend can't reach backend | CORS not configured | Check CORS_ALLOWED_ORIGINS in `.env` |
| Port 8000 already in use | Another app using it | `netstat -ano \| findstr :8000` to find PID |
| Port 5173 already in use | Vite using different port | Check terminal output for actual port |
| Email sends from console | Using console backend | Set EMAIL_BACKEND to SMTP in `.env` |

---

## 📱 Project Access

Once running:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/v1/ (browsable)

---

## 🔐 Production Before Going Live

1. Set `DJANGO_DEBUG=false`
2. Use strong `DJANGO_SECRET_KEY`
3. Enable HTTPS
4. Add production Gmail or SendGrid
5. Update OAuth redirect URIs to production domain
6. Run `collectstatic`: `python manage.py collectstatic`
7. Use proper database (production MySQL)
8. Set up logging and monitoring
9. Enable rate limiting
10. Use environment variables (not in code)

---

## 📞 Quick Command Reference

```powershell
# Backend Setup
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8000

# Frontend Setup
cd frontend
npm install
npm run dev

# Shell Access
python manage.py shell
python manage.py shell_plus  # with IPython

# Create Superuser
python manage.py createsuperuser

# Database
python manage.py dbshell  # MySQL prompt
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

---

## ✅ Verification Checklist

After setup, you should see:

✓ Backend: "Starting development server at http://127.0.0.1:8000/"
✓ Frontend: "Local: http://localhost:5173/"
✓ No console errors in browser
✓ Can navigate to login page
✓ Emails send (console or Gmail)
✓ Google button appears on login page
✓ Can complete all authentication flows

**Status**: All systems ready! 🚀
