# 🔧 Fix OAuth Error 401: invalid_client

## Root Cause
Your `.env` files still have placeholder Google credentials:
- `GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com` ❌
- `GOOGLE_OAUTH_CLIENT_SECRET=your-secret` ❌

---

## ✅ Step-by-Step: Get Real Google OAuth Credentials

### Step 1: Go to Google Cloud Console
**URL**: https://console.cloud.google.com

### Step 2: Create a Project (if needed)
1. Click "Select a Project" at top
2. Click "New Project"
3. Enter name: `net-bank` or similar
4. Click "Create"
5. Wait for project to be created

### Step 3: Enable Google+ API
1. In search bar, type: `Google+ API`
2. Click "Google+ API"
3. Click "Enable"

### Step 4: Create OAuth 2.0 Credentials
1. Go to **Credentials** (left sidebar)
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted: **Configure OAuth consent screen first**
   - Click **Configure Consent Screen**
   - Select **External** user type
   - Click **Create**
   - Fill in:
     - **App name**: Net Bank
     - **User support email**: your-email@gmail.com
     - **Developer contact**: your-email@gmail.com
   - Click **Save and Continue** (skip optional sections)
   - Click **Back to Credentials**

4. Now create OAuth credentials:
   - Click **Create Credentials** → **OAuth client ID**
   - Select **Web Application**
   - Give it a name: `Net Bank Local` or similar
   - Under **Authorized redirect URIs**, add BOTH:
     ```
     http://localhost:5173/auth/google/callback
     http://127.0.0.1:5173/auth/google/callback
     ```
   - Click **Create**

### Step 5: Copy Your Credentials
You'll see a popup with:
- **Client ID** → Copy this
- **Client Secret** → Copy this

**Example output:**
```
Client ID: 123456789-abcdefghijklmnop.apps.googleusercontent.com
Client Secret: your-client-secret
```

---

## 🔑 Update Your .env Files

### File 1: Backend
**Location**: `d:\programme files\net-bank\backend\.env`

Find these lines:
```
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-secret
```

Replace with YOUR actual credentials:
```
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

### File 2: Frontend
**Location**: `d:\programme files\net-bank\frontend\.env`

Find this line:
```
VITE_GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

Replace with YOUR Client ID:
```
VITE_GOOGLE_OAUTH_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

---

## ⚙️ After Updating .env

### 1. Restart Backend
```powershell
# In backend terminal, press Ctrl+C to stop
# Then run again:
python manage.py runserver 8000
```

### 2. Restart Frontend
```powershell
# In frontend terminal, press Ctrl+C to stop
# Then run again:
npm run dev
```

### 3. Clear Browser Cache
In browser:
```javascript
// Open Developer Tools (F12)
// Go to Console tab, paste:
localStorage.clear()
sessionStorage.clear()
// Refresh page
```

### 4. Try Again
1. Go to http://localhost:5173/auth/login
2. Click "Continue with Google"
3. Should work now! ✓

---

## 🚨 Common Mistakes

| Mistake | Fix |
|---------|-----|
| Redirect URI is `https://` instead of `http://` | Must be `http://localhost:5173/auth/google/callback` (local) |
| Forgot to click "Enable" on Google+ API | Go back and enable it |
| Client ID and Secret swapped | Copy Client ID to frontend, both to backend |
| Didn't restart backend/frontend | Must restart after changing .env |
| Browser cache has old values | Clear cache with `localStorage.clear()` |

---

## ✅ Verify Credentials Are Correct

### Backend Check
Open `backend/.env` and verify:
```
GOOGLE_OAUTH_CLIENT_ID=xxx-yyy.apps.googleusercontent.com  (NOT "your-client-id")
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret  (use the value from your secret manager)
```

### Frontend Check
Open `frontend/.env` and verify:
```
VITE_GOOGLE_OAUTH_CLIENT_ID=xxx-yyy.apps.googleusercontent.com  (NOT "your-client-id")
```

---

## 🧪 Test OAuth Flow

1. **Login page**: http://localhost:5173/auth/login
2. **Click**: "Continue with Google" button
3. **Redirect**: Google login page should appear
4. **Select**: Your Google account
5. **Authorize**: Click "Continue"
6. **Redirect back**: Should go to dashboard with tokens
7. **Success**: You're logged in! ✓

---

## 🆘 Still Getting Error?

If you still see `Error 401: invalid_client`:

1. **Check exact values match**
   - Copy Client ID directly from Google (no spaces/typos)
   - Copy Secret directly from Google
   - Paste into `.env` exactly

2. **Verify redirect URI**
   - Google Console: `http://localhost:5173/auth/google/callback`
   - Frontend code: `/auth/google/callback` ✓
   - Backend settings: `FRONTEND_URL=http://localhost:5173` ✓

3. **Check both files are updated**
   - `backend/.env` ← Has Client ID and Secret
   - `frontend/.env` ← Has Client ID

4. **Restart everything**
   - Stop backend (Ctrl+C)
   - Stop frontend (Ctrl+C)
   - Restart backend: `python manage.py runserver 8000`
   - Restart frontend: `npm run dev`

5. **Clear cache**
   - Browser: Ctrl+Shift+Delete
   - localStorage: `localStorage.clear()` in console

---

## 📋 Checklist

- [ ] Created Google Cloud project
- [ ] Enabled Google+ API
- [ ] Created OAuth 2.0 credentials (Web Application)
- [ ] Added redirect URI: `http://localhost:5173/auth/google/callback`
- [ ] Copied Client ID to backend `.env`
- [ ] Copied Client Secret to backend `.env`
- [ ] Copied Client ID to frontend `.env`
- [ ] Restarted backend server
- [ ] Restarted frontend server
- [ ] Cleared browser cache
- [ ] Tested OAuth flow

**Status**: Ready for OAuth! 🎉
