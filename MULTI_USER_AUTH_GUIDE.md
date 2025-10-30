# Multi-User Authentication Guide 🔐

## Secure Authentication Strategies for Streamlit Multi-User App

---

## 🎯 The Challenge

When multiple users access your Streamlit app on Streamlit Cloud:
- Each user needs their own Draftr authentication
- Automation runs on the **server**, not user's machine
- Cannot access user's local browser session
- Need secure per-user credential management

---

## ✅ Solution 1: OAuth Token Delegation (Recommended)

### Architecture:

```
User → Streamlit (OAuth) → Get Token → Use Token → Draftr API/Browser
```

### Implementation:

#### Step 1: Add OAuth to Streamlit

```python
import streamlit as st
from streamlit_oauth import OAuth2Component
import os

# Configure Autodesk OAuth
oauth2 = OAuth2Component(
    client_id=os.getenv("AUTODESK_CLIENT_ID"),
    client_secret=os.getenv("AUTODESK_CLIENT_SECRET"),
    authorize_endpoint="https://developer.api.autodesk.com/authentication/v2/authorize",
    token_endpoint="https://developer.api.autodesk.com/authentication/v2/token",
    refresh_token_endpoint="https://developer.api.autodesk.com/authentication/v2/token",
    client_kwargs={"scope": "data:read data:write"}
)

# Check if user is authenticated
if 'token' not in st.session_state:
    # Show login button
    result = oauth2.authorize_button(
        name="Login with Autodesk",
        redirect_uri="https://your-app.streamlit.app/callback"
    )
    
    if result:
        st.session_state.token = result.get('token')
        st.session_state.user_email = result.get('email')
        st.rerun()
else:
    st.success(f"✅ Logged in as: {st.session_state.user_email}")
```

#### Step 2: Pass Token to Playwright

Modify `mdc_executor.js` to use the token:

```javascript
// In mdc_executor.js
async startMCPConnection(authToken) {
    const env = {
        ...process.env,
        AUTODESK_AUTH_TOKEN: authToken,  // Pass user's token
        PLAYWRIGHT_HEADLESS: '1'
    };
    
    // ... rest of code
}
```

#### Step 3: Inject Token into Browser

Add to MDC file:

```mcp
### Step 0.1: Set authentication token
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => { localStorage.setItem('autodesk_token', process.env.AUTODESK_AUTH_TOKEN); document.cookie = `Bearer=${process.env.AUTODESK_AUTH_TOKEN}; domain=.autodesk.com; path=/`; }"
  }
}
```

### Advantages:

✅ **Per-user authentication** - Each user uses their own credentials
✅ **Secure** - No shared passwords, tokens managed by OAuth
✅ **Audit trail** - Know who made each change
✅ **Permissions** - Respects user's Draftr permissions
✅ **Token refresh** - Auto-refresh expired tokens

### Security:

- ✅ Tokens stored in user's session only
- ✅ Tokens expire automatically
- ✅ User can revoke access anytime
- ✅ No passwords stored anywhere

---

## ✅ Solution 2: Per-User Secrets (Simple but Secure)

### Architecture:

```
User → Enter Credentials → Store in Session → Use for Automation
```

### Implementation:

#### Step 1: User Login UI

```python
import streamlit as st
import hashlib

def authenticate_user():
    """Let user enter their Draftr credentials"""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.subheader("🔐 Draftr Authentication")
        
        with st.form("login_form"):
            email = st.text_input("Draftr Email", type="default")
            password = st.text_input("Draftr Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if email and password:
                    # Store hashed credentials in session
                    st.session_state.draftr_email = email
                    st.session_state.draftr_password = password
                    st.session_state.authenticated = True
                    st.success("✅ Authenticated!")
                    st.rerun()
                else:
                    st.error("Please enter both email and password")
    else:
        st.success(f"✅ Logged in as: {st.session_state.draftr_email}")
        if st.button("Logout"):
            # Clear credentials from session
            st.session_state.clear()
            st.rerun()
```

#### Step 2: Pass Credentials Securely

```python
def execute_with_user_auth(mdc_path, variables):
    """Execute MDC with user's credentials"""
    
    if not st.session_state.get('authenticated'):
        st.error("❌ Please login first")
        return
    
    # Pass credentials as variables
    context = {
        "variables": {
            **variables,
            "draftr_email": st.session_state.draftr_email,
            "draftr_password": st.session_state.draftr_password
        }
    }
    
    # Execute MDC
    result = mdc_executor.execute_mdc_file(mdc_path, context)
    
    return result
```

#### Step 3: Login Phase in MDC

Add this at the start of `draftr-link-updater-js.mdc`:

```mcp
## PHASE 0: User Authentication

### Step 0.1: Navigate to Autodesk Login
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://accounts.autodesk.com/Authentication/LogIn"
  }
}
```

```mcp
### Step 0.2: Wait for login page
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 2000))"
  }
}
```

```mcp
### Step 0.3: Fill email
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[type='email'], input#userName",
    "value": "{{draftr_email}}"
  }
}
```

```mcp
### Step 0.4: Click Next/Continue
{
  "tool": "playwright_click",
  "params": {
    "selector": "button[type='submit'], button#verify_user_btn"
  }
}
```

```mcp
### Step 0.5: Wait for password field
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 2000))"
  }
}
```

```mcp
### Step 0.6: Fill password
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[type='password'], input#password",
    "value": "{{draftr_password}}"
  }
}
```

```mcp
### Step 0.7: Click Sign In
{
  "tool": "playwright_click",
  "params": {
    "selector": "button[type='submit'], button#btnSubmit"
  }
}
```

```mcp
### Step 0.8: Wait for login to complete
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 5000))"
  }
}
```

```mcp
### Step 0.9: Verify login success
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => { const isLoggedIn = !window.location.href.includes('login') && !window.location.href.includes('authentication'); return { isLoggedIn: isLoggedIn, currentUrl: window.location.href, timestamp: new Date().toISOString() }; }"
  }
}
```

### Advantages:

✅ **Simple to implement** - Just add login form
✅ **Per-user credentials** - Each user uses their own
✅ **No shared secrets** - Credentials only in user's session
✅ **Works immediately** - No OAuth setup required

### Security Features:

- ✅ Credentials stored in **session only** (not in database)
- ✅ Session cleared on logout
- ✅ HTTPS encryption in transit
- ✅ No credentials in logs
- ✅ User controls their own password

---

## ✅ Solution 3: Service Account (Single Shared Account)

### When to Use:

- **Internal tool** (small team only)
- **Admin-only** operations
- **Don't need per-user tracking**

### Implementation:

```python
# In app.py
import streamlit as st

# Admin authentication
admin_password = st.secrets["admin"]["password"]

with st.sidebar:
    entered_password = st.text_input("Admin Password", type="password")
    
    if entered_password == admin_password:
        st.success("✅ Admin authenticated")
        st.session_state.is_admin = True
    elif entered_password:
        st.error("❌ Invalid password")
```

Store service account in `.streamlit/secrets.toml`:

```toml
[draftr_service_account]
email = "draftr-automation@yourcompany.com"
password = "secure-password-here"

[admin]
password = "admin-access-password"
```

### Advantages:

✅ **Simplest setup** - One account for all users
✅ **No per-user login** - Users authenticate to Streamlit only

### Disadvantages:

❌ **No user tracking** - Can't tell who made changes
❌ **Shared permissions** - All users have same access
❌ **Security risk** - One compromised password affects all

---

## 🎯 Comparison Table

| Solution | Setup Difficulty | Security | Per-User | Best For |
|----------|-----------------|----------|----------|----------|
| **OAuth Token** | 🟡 Medium | 🟢 Excellent | ✅ Yes | Production, many users |
| **Per-User Login** | 🟢 Easy | 🟢 Good | ✅ Yes | Most use cases |
| **Service Account** | 🟢 Very Easy | 🟡 Fair | ❌ No | Small teams, internal |

---

## 🔒 Security Best Practices

### DO:

✅ **Use HTTPS** - Streamlit Cloud provides this automatically
✅ **Session-based storage** - Store credentials in `st.session_state` only
✅ **Clear on logout** - Always clear session data
✅ **Encrypt at rest** - Use Streamlit Secrets for any stored credentials
✅ **Audit logging** - Track who does what
✅ **Token expiration** - Use short-lived tokens
✅ **MFA support** - Handle 2FA if Draftr requires it

### DON'T:

❌ **Store in database** - Passwords should never be in DB
❌ **Log credentials** - Never print passwords in logs
❌ **Share sessions** - Each user should have their own session
❌ **Cache credentials** - Don't store beyond session lifetime
❌ **Commit secrets** - Never commit credentials to Git

---

## 💡 Recommended Approach

### For Your Use Case:

**Recommended: Solution 2 (Per-User Login)**

**Why:**
1. ✅ **Secure** - Each user uses their own Draftr credentials
2. ✅ **Simple** - No OAuth setup required
3. ✅ **Audit trail** - Know who made each change
4. ✅ **Quick to implement** - Add login form + login phase to MDC
5. ✅ **User control** - Users manage their own passwords

### Implementation Plan:

1. **Add login form** to Streamlit UI (5 minutes)
2. **Store credentials** in session state (2 minutes)
3. **Add login phase** to MDC file (10 minutes)
4. **Test locally** with your credentials (5 minutes)
5. **Deploy to Streamlit Cloud** (automatic)

**Total setup time: ~25 minutes**

---

## 🧪 Testing Multi-User Setup

### Test Scenario 1: User A

```python
# User A logs in
email: "user-a@company.com"
password: "password-a"

# Runs automation
prompt: "run js mdc on asset/123 ..."

# Result: Uses User A's Draftr permissions
```

### Test Scenario 2: User B

```python
# User B logs in
email: "user-b@company.com"
password: "password-b"

# Runs automation
prompt: "run js mdc on asset/456 ..."

# Result: Uses User B's Draftr permissions
```

### Test Scenario 3: Logout/Login

```python
# User A logs in
# Runs automation
# Logs out → Session cleared
# User B logs in
# Runs automation → Different credentials used
```

---

## 🎓 Understanding Session vs Browser Session

### Important Clarification:

**What DOESN'T Work:**
```
❌ User's local browser cookies → Can't access from Streamlit Cloud
❌ User's Chrome profile → Not available on remote server
❌ User's existing Draftr session → Different machine entirely
```

**What DOES Work:**
```
✅ User enters credentials → Stored in session
✅ Playwright logs in → Using those credentials
✅ Automation runs → With user's permissions
✅ Session expires → User logs in again
```

---

## 🚀 Quick Start Implementation

### Add This to Your `app.py`:

```python
import streamlit as st

def require_authentication():
    """Simple per-user authentication"""
    
    if 'draftr_credentials' not in st.session_state:
        st.session_state.draftr_credentials = None
    
    if not st.session_state.draftr_credentials:
        st.subheader("🔐 Login to Draftr")
        
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Draftr Email")
        with col2:
            password = st.text_input("Draftr Password", type="password")
        
        if st.button("Login"):
            if email and password:
                st.session_state.draftr_credentials = {
                    "email": email,
                    "password": password
                }
                st.success("✅ Logged in!")
                st.rerun()
            else:
                st.error("Please enter both email and password")
        
        st.stop()  # Don't show rest of app until logged in
    
    else:
        # Show logout option
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ Logged in as: {st.session_state.draftr_credentials['email']}")
        with col2:
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

# Call at the start of your app
require_authentication()

# Rest of your app code...
```

---

## 📊 Security Checklist

### Before Deployment:

- [ ] Credentials stored in session only
- [ ] HTTPS enabled (Streamlit Cloud default)
- [ ] Logout clears all session data
- [ ] No credentials in logs
- [ ] No credentials in Git
- [ ] Session timeout implemented
- [ ] Error messages don't leak info
- [ ] Rate limiting considered

---

## ✅ Summary

### Can We Use User's Existing Browser Session?

**Short Answer:** No, not on Streamlit Cloud (different machines)

**Long Answer:** 
- **Local testing:** Yes, can use persistent browser context
- **Streamlit Cloud:** No, server can't access user's local cookies
- **Solution:** User logs in through Streamlit, automation uses those credentials

### Will Each User Need to Authenticate?

**Yes, and that's BETTER for security:**

✅ **Each user controls their own credentials**
✅ **Audit trail shows who did what**
✅ **Users have their own permissions**
✅ **No shared password risk**
✅ **User can change their password anytime**

### Recommended Approach:

**Per-User Login (Solution 2):**
- Simple to implement
- Secure and isolated
- Good audit trail
- Works immediately

**Next Steps:**
1. Add login form to `app.py` (copy code above)
2. Add login phase to MDC file
3. Test locally
4. Deploy!

🎉 **Ready to implement? I can help you add the login form right now!**

