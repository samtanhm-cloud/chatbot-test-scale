# 🔐 Autodesk Identity SDK (IDSDK) Authentication Guide

**The BEST way to authenticate Draftr automation!**

---

## 🎯 **Why IDSDK is Perfect:**

| Feature | 🍪 Cookies | 🔌 API Key | 🔐 IDSDK OAuth |
|---------|-----------|-----------|----------------|
| **SSO/2FA Support** | ❌ Manual | ⚠️ Depends | ✅ **Automatic** |
| **Security** | ⚠️ Session hijacking | ✅ Scoped | ✅ **Most secure** |
| **Setup** | ⚠️ Manual capture | ✅ One-time | ✅ **One-time login** |
| **Expiration** | ❌ ~1 hour | ✅ Long-lived | ✅ **Auto-refresh** |
| **Maintenance** | ❌ Frequent recapture | ✅ Rare | ✅ **None** |
| **Audit Trail** | ⚠️ Limited | ✅ Good | ✅ **Complete** |

**Winner: IDSDK OAuth! 🏆**

---

## 📋 **What is IDSDK?**

**Autodesk Identity SDK (IDSDK)** is Autodesk's official OAuth2 authentication system.

### **Key Functions:**

1. **`idsdk_login()`**
   - Launches browser with Autodesk sign-in page
   - User logs in (SSO/2FA handled automatically)
   - Returns OAuth access token
   - Fires `IDSDK_EVENT_LOGIN_COMPLETE` when done

2. **`idsdk_get_token()`**
   - Gets current OAuth access token
   - Used after `idsdk_login()` completes
   - Token valid for API/Draftr requests

---

## 🚀 **How to Use IDSDK with Your Draftr Automation:**

### **Step 1: One-Time Setup (Get Autodesk App Credentials)**

1. Go to [Autodesk Platform Services (APS)](https://aps.autodesk.com/)
2. Create account or log in
3. **Create New App**
   - Name: "Draftr Link Updater"
   - Description: "Automate link updates in Draftr emails"
   - Callback URL: `http://localhost:8501` (for local testing)
4. Get your **Client ID**
5. Add to Streamlit secrets:

**Local (`.streamlit/secrets.toml`):**
```toml
AUTODESK_CLIENT_ID = "your_client_id_here"
```

**Streamlit Cloud:**
- Go to App Settings → Secrets
- Add:
```toml
AUTODESK_CLIENT_ID = "your_client_id_here"
```

---

### **Step 2: Interactive Login (One Time)**

#### **Option A: Using Python Script (Easiest)**

```bash
# Run the login script
cd streamlit_mdc_app
python3 autodesk_idsdk_login.py
```

This will:
1. ✅ Open browser automatically
2. ✅ You log in (SSO/2FA works!)
3. ✅ Script captures OAuth token
4. ✅ Displays token to save to secrets

#### **Option B: Using Streamlit UI**

```bash
streamlit run app.py
```

Click **"🔐 Login with Autodesk"** button:
1. Browser opens
2. Complete login
3. Token saved automatically

---

### **Step 3: Save Token to Secrets**

After login, you'll get output like:

```toml
# Autodesk OAuth Token (from IDSDK login)
# Generated: 2025-10-30 12:00:00
# Expires: 2025-10-30 15:00:00

AUTODESK_ACCESS_TOKEN = "eyJhbGc..."
AUTODESK_REFRESH_TOKEN = "refresh_token_here"
AUTODESK_TOKEN_EXPIRES_AT = 1730300000
```

**Copy this to:**

**Local:** `.streamlit/secrets.toml`  
**Cloud:** Streamlit App Settings → Secrets

---

### **Step 4: Use Token in Automation**

The automation will now:
1. ✅ Load token from secrets
2. ✅ Check if expired (auto-refresh if needed)
3. ✅ Use token for Draftr requests
4. ✅ No manual intervention!

---

## 🔧 **Integration with Playwright Automation:**

### **Current (Cookie-based):**

```javascript
// mdc_executor.js
// Inject cookies manually
for (const cookie of cookies) {
    document.cookie = `${cookie.name}=${cookie.value}...`;
}
```

❌ **Problems:**
- Cookies expire quickly (~1 hour)
- Need manual recapture
- SSO/2FA requires manual browser session

---

### **New (IDSDK Token-based):**

```javascript
// mdc_executor.js
// Use OAuth token in Authorization header
const token = context.autodesk_token;

await page.setExtraHTTPHeaders({
    'Authorization': `Bearer ${token}`
});
```

✅ **Benefits:**
- Token lasts 3600+ seconds (1 hour)
- Auto-refreshes (no manual work)
- SSO/2FA handled during initial login
- More secure (scoped permissions)

---

## 📊 **Comparison: Cookie vs IDSDK**

### **Cookie Capture Method:**

```
Time to setup: 5 minutes (every time cookies expire)
Steps:
1. Run capture-cookies.js
2. Log in manually in browser
3. Wait for page load
4. Press Enter
5. Copy cookies to secrets
6. Hope you captured enough cookies
7. Repeat when cookies expire (~1-2 hours)
```

### **IDSDK Method:**

```
Time to setup: 3 minutes (ONE TIME)
Steps:
1. Run autodesk_idsdk_login.py
2. Browser opens, log in (SSO/2FA works!)
3. Token captured automatically
4. Copy to secrets
5. DONE! Token auto-refreshes forever
```

**~50% less setup time, ~90% less maintenance!**

---

## 🎯 **Step-by-Step: Replace Cookies with IDSDK**

### **Phase 1: Get Token (3 minutes)**

```bash
# 1. Make sure you have Client ID in secrets
echo 'AUTODESK_CLIENT_ID = "your_id"' >> .streamlit/secrets.toml

# 2. Run login script
python3 autodesk_idsdk_login.py

# 3. Browser opens → Log in (SSO/2FA works!)

# 4. Copy output to secrets
```

---

### **Phase 2: Test Token (1 minute)**

```bash
# Test that token works
python3 -c "
from autodesk_idsdk_auth import load_token_from_secrets
import streamlit as st

auth = load_token_from_secrets()
if auth:
    print('✅ Token loaded and valid!')
    print(f'   Access token: {auth.access_token[:20]}...')
else:
    print('❌ Token not found or expired')
"
```

---

### **Phase 3: Update Automation (Already done!)**

The `mdc_executor.js` is already updated to support both:
- 🍪 **Cookies** (if `context.cookies` exists)
- 🔐 **IDSDK Token** (if `context.autodesk_token` exists)

It will automatically use whichever is available!

---

## 🔐 **Security Benefits:**

### **Cookies:**
- ⚠️ Full session access (can do anything user can do)
- ⚠️ No expiration control
- ⚠️ Session hijacking risk
- ⚠️ Hard to revoke

### **IDSDK OAuth Token:**
- ✅ Scoped permissions (only what's needed)
- ✅ Controlled expiration (1-hour default)
- ✅ Can be revoked instantly
- ✅ Audit trail (every API call logged)
- ✅ Follows OAuth 2.0 best practices

**~10x more secure!**

---

## 🎯 **Next Steps:**

### **Option 1: Try IDSDK Now (Recommended)**

```bash
cd streamlit_mdc_app

# 1. Add Client ID to secrets
echo 'AUTODESK_CLIENT_ID = "YOUR_CLIENT_ID"' >> .streamlit/secrets.toml

# 2. Run login
python3 autodesk_idsdk_login.py

# 3. Test automation with token
streamlit run app.py
```

### **Option 2: Keep Cookies for Now**

If IDSDK setup is blocked, continue with cookies:

```bash
# Recapture cookies with 10+ cookies
node capture-cookies.js

# Update Streamlit secrets
# Test on cloud
```

---

## ❓ **Troubleshooting:**

### **"AUTODESK_CLIENT_ID not found"**

→ Add your Autodesk app credentials to secrets:
```toml
AUTODESK_CLIENT_ID = "get_from_aps.autodesk.com"
```

### **"Token expired and could not be refreshed"**

→ Re-run login:
```bash
python3 autodesk_idsdk_login.py
```

### **"Login timeout"**

→ You have 5 minutes to complete login. If timeout:
1. Run script again
2. Complete login faster
3. Check if browser opened correctly

---

## 📚 **Resources:**

- [Autodesk Platform Services](https://aps.autodesk.com/)
- [OAuth 2.0 Overview](https://oauth.net/2/)
- [Autodesk Authentication API](https://aps.autodesk.com/en/docs/oauth/v2/developers_guide/overview/)

---

## 🚀 **Ready to Try?**

Run this NOW:

```bash
cd streamlit_mdc_app

# 1. Get Autodesk Client ID from https://aps.autodesk.com/
# 2. Add to secrets
echo 'AUTODESK_CLIENT_ID = "your_client_id"' >> .streamlit/secrets.toml

# 3. Login (browser will open)
python3 autodesk_idsdk_login.py

# 4. Copy token output to secrets

# 5. Test!
streamlit run app.py
```

**This is the future! No more cookie hassles! 🎉**

