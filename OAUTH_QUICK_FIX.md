# ⚡ Quick OAuth Fix Checklist

## 🚨 Error: 401 invalid_client
Your Google OAuth credentials are placeholders. Here's the quick fix:

---

## 5-Minute Setup

### ✅ STEP 1: Get Credentials (2 min)
Go to: https://console.cloud.google.com
1. Create new project
2. Search & enable "Google+ API"
3. Go to Credentials → Create OAuth 2.0 (Web Application)
4. Add redirect: `http://localhost:5173/auth/google/callback`
5. Copy:
   - **Client ID**: `abc123-xxx.apps.googleusercontent.com`
   - **Client Secret**: your client secret

### ✅ STEP 2: Update Backend .env (1 min)
File: `d:\programme files\net-bank\backend\.env`

Replace:
```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-secret
```

With:
```
GOOGLE_OAUTH_CLIENT_ID=abc123-xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

### ✅ STEP 3: Update Frontend .env (30 sec)
File: `d:\programme files\net-bank\frontend\.env`

Replace:
```
VITE_GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

With:
```
VITE_GOOGLE_OAUTH_CLIENT_ID=abc123-xxx.apps.googleusercontent.com
```

### ✅ STEP 4: Restart (1 min)
```powershell
# Terminal 1 - Backend
# Press Ctrl+C to stop
python manage.py runserver 8000

# Terminal 2 - Frontend
# Press Ctrl+C to stop
npm run dev
```

### ✅ STEP 5: Test (1 min)
1. Go to http://localhost:5173/auth/login
2. Click "Continue with Google"
3. Should work! ✓

---

## ❌ If Still Error

- [ ] Credentials are real (not "your-client-id")
- [ ] Redirect URI matches: `http://localhost:5173/auth/google/callback`
- [ ] Restarted BOTH backend and frontend
- [ ] Cleared browser cache: `localStorage.clear()`

---

## 📝 Credentials Template

**From Google Console:**
```
Client ID:     [Your 123-xxx.apps.googleusercontent.com]
Client Secret: [your client secret]
```

**In backend/.env:**
```
GOOGLE_OAUTH_CLIENT_ID=[paste Client ID here]
GOOGLE_OAUTH_CLIENT_SECRET=[paste Client Secret here]
```

**In frontend/.env:**
```
VITE_GOOGLE_OAUTH_CLIENT_ID=[paste Client ID here]
```

---

**Done!** OAuth should now work. 🎉
