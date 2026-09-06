# ⚡ Quick Fix - Your 3 Issues

## Issue 1: OTP Login Not Working
**Cause**: Email credentials in backend `.env` are placeholders
**Fix**: 
```
EMAIL_HOST_USER=your-actual-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```
Get app password from: https://myaccount.google.com/apppasswords

---

## Issue 2: Forgot Password Not Working  
**Same cause as Issue 1** - Email credentials needed
```
# Update backend/.env with real Gmail credentials
```

---

## Issue 3: OAuth Client Error (401: invalid_client)
**Cause**: Google OAuth credentials in backend `.env` are placeholders
**Fix**:
1. Go to https://console.cloud.google.com
2. Create OAuth credentials (Web Application type)
3. Add redirect: `http://localhost:5173/auth/google/callback`
4. Copy Client ID and Secret
5. Update backend/.env:
```
GOOGLE_OAUTH_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```
6. Update frontend/.env (already created):
```
VITE_GOOGLE_OAUTH_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
```

---

## ✅ How to Run Whole Project

### Terminal 1 - Backend
```powershell
cd "d:\programme files\net-bank\backend"
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

### Terminal 2 - Frontend
```powershell
cd "d:\programme files\net-bank\frontend"
npm install
npm run dev
```

**Done!** 
- Backend: http://127.0.0.1:8000/
- Frontend: http://localhost:5173/

---

## 🧪 Test After Setup

1. **Register**: Go to http://localhost:5173/auth/register
2. **OTP Login**: Go to http://localhost:5173/auth/otp-login → Email with OTP
3. **Forgot Password**: Go to http://localhost:5173/auth/forgot-password → Email with link
4. **Google Login**: Click "Continue with Google" button

---

## 📝 Quick Reference

**Backend .env needs:**
- `GOOGLE_OAUTH_CLIENT_ID` ← From Google Console
- `GOOGLE_OAUTH_CLIENT_SECRET` ← From Google Console
- `EMAIL_HOST_USER` ← Your Gmail
- `EMAIL_HOST_PASSWORD` ← Gmail app password

**Frontend .env needs:**
- `VITE_GOOGLE_OAUTH_CLIENT_ID` ← Same as backend

**Status**: ✓ Backend running, ⏳ Awaiting credentials
