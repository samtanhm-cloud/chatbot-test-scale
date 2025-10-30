# Authentication Guide 🔐

## How Authentication Works with Playwright

---

## 🎯 Overview

When Playwright automates Draftr, it needs to be **authenticated** (logged in) to access and modify assets. Here's how it works:

---

## 🌐 Two Scenarios

### Scenario 1: Local Testing (Your Computer)
**Status:** ✅ **Easy - Authentication works automatically!**

### Scenario 2: Streamlit Cloud (Headless Server)
**Status:** ⚠️ **Requires setup - No browser session available**

---

## 📋 Scenario 1: Local Testing

### How It Works:

When you run the automation **on your local machine**:

1. **You're already logged into Draftr** in your regular browser (Chrome/Edge/Firefox)
2. **Playwright launches a browser** that can access your session
3. **Your authentication cookies are available** to Playwright
4. **Automation runs with your credentials** automatically

### Example:

```
You (logged into Draftr) → Run automation → Playwright uses your session → Works! ✅
```

### Why It Works:

- Playwright can use **persistent browser context** that shares cookies with your regular browser
- Or use **browser profile** that has your existing session
- **No additional authentication needed!**

---

## 📋 Scenario 2: Streamlit Cloud (Production)

### The Challenge:

When running on **Streamlit Cloud** in **headless mode**:

1. ❌ **No existing browser session** (server has never logged into Draftr)
2. ❌ **No stored cookies** (fresh browser every time)
3. ❌ **Can't see login page** (headless mode = no visual interface)

### The Problem:

```
Streamlit Cloud → Launches headless browser → No session → Draftr shows login page → Automation fails ❌
```

---

## ✅ Solutions for Streamlit Cloud

### Option 1: Session Cookies (Recommended)

**Store your authentication cookies and inject them:**

#### Step 1: Get Your Cookies

1. **Login to Draftr** in your browser
2. **Open Chrome DevTools** (F12)
3. **Go to Application tab** → Cookies → `https://webpub.autodesk.com`
4. **Copy these cookies:**
   - `ADSK_AUTH_TOKEN` (or similar)
   - `session_id`
   - Any other authentication cookies

#### Step 2: Store in Streamlit Secrets

Add to `.streamlit/secrets.toml`:

```toml
[draftr]
auth_cookies = '''
{
  "ADSK_AUTH_TOKEN": "your-token-here",
  "session_id": "your-session-id",
  "_ga": "GA1.2.xxx"
}
'''
```

#### Step 3: Modify MDC to Inject Cookies

Add this **before** navigating to Draftr:

```mcp
### Step 0.1: Set authentication cookies
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => { const cookies = JSON.parse(process.env.DRAFTR_COOKIES || '{}'); Object.entries(cookies).forEach(([name, value]) => { document.cookie = `${name}=${value}; domain=.autodesk.com; path=/`; }); }"
  }
}
```

---

### Option 2: Programmatic Login

**Add login steps at the beginning:**

#### Add Login Phase to MDC:

```mcp
## PHASE 0: Authentication

### Step 0.1: Navigate to Draftr login
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://webpub.autodesk.com/draftr/login"
  }
}
```

```mcp
### Step 0.2: Fill username
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[name='username']",
    "value": "{{draftr_username}}"
  }
}
```

```mcp
### Step 0.3: Fill password
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[name='password']",
    "value": "{{draftr_password}}"
  }
}
```

```mcp
### Step 0.4: Click login button
{
  "tool": "playwright_click",
  "params": {
    "selector": "button[type='submit']"
  }
}
```

```mcp
### Step 0.5: Wait for login to complete
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 5000))"
  }
}
```

**Store credentials in `.streamlit/secrets.toml`:**

```toml
[draftr]
username = "your-email@autodesk.com"
password = "your-secure-password"
```

---

### Option 3: SSO/SAML (If Draftr uses SSO)

**If Draftr uses Autodesk SSO:**

This is more complex and requires:
1. Understanding the SSO flow
2. Capturing OAuth tokens
3. Handling redirects

**Not recommended for automation** - use cookies or API instead.

---

### Option 4: Draftr API Token (Best for Production)

**If Draftr has an API:**

Instead of browser automation, use API calls:

```python
import requests

headers = {
    "Authorization": f"Bearer {draftr_api_token}",
    "Content-Type": "application/json"
}

# Update link via API
response = requests.patch(
    f"https://api.draftr.autodesk.com/assets/{asset_id}/links",
    headers=headers,
    json={"link_id": "123", "new_url": "https://example.com"}
)
```

**Advantages:**
- ✅ No browser needed (faster)
- ✅ More reliable
- ✅ Easier authentication (just API token)
- ✅ Better for production

---

## 🔒 Security Best Practices

### DO:
✅ Store credentials in **Streamlit Secrets** (never in code)
✅ Use **environment variables** for sensitive data
✅ Rotate cookies/tokens regularly
✅ Use API tokens when possible
✅ Limit permissions to minimum needed

### DON'T:
❌ Commit credentials to Git
❌ Share your authentication tokens
❌ Store passwords in plain text
❌ Use your personal account for automation (create a service account)
❌ Log sensitive data

---

## 🧪 Testing Authentication

### Test Locally First:

```bash
# Run locally to test (uses your browser session)
streamlit run app.py
```

**If it works locally:**
- ✅ Automation logic is correct
- ✅ Selectors are correct
- ✅ Only authentication needs setup for cloud

### Test Cookie Injection:

```javascript
// In Chrome Console on Draftr page
document.cookie = "test_cookie=test_value; path=/"
console.log(document.cookie) // Should show test_cookie
```

---

## 📊 Authentication Flow Diagram

### Local (Works Automatically):
```
Your Browser (logged in)
    ↓
Playwright launches
    ↓
Uses your session cookies
    ↓
Automation runs authenticated ✅
```

### Streamlit Cloud (Needs Setup):
```
Streamlit Cloud Server
    ↓
Playwright launches (headless)
    ↓
No cookies → Login page shown ❌
    ↓
Solution: Inject cookies OR Login programmatically
    ↓
Automation runs authenticated ✅
```

---

## 🎯 Recommended Approach

### For Development/Testing:
**Use Local Testing** - Your existing session works automatically

### For Production on Streamlit Cloud:
**Option A:** Inject session cookies (fastest setup)
**Option B:** Add programmatic login (more reliable long-term)
**Option C:** Use Draftr API if available (best for production)

---

## 🚨 Current Status

### What's Implemented:
✅ MDC file ready with Save button automation
✅ All three operation types (change_specific, replace_all, replace_domain)
✅ Variable extraction and substitution
✅ Comprehensive error logging

### What Needs Setup for Streamlit Cloud:
⚠️ **Authentication** - Choose one option above

### How to Test:
1. **Local first:** Run on your machine - should work automatically
2. **If it works locally:** Authentication works
3. **For Streamlit Cloud:** Add cookie injection or login phase

---

## 💡 Quick Start

### Test Locally Now (No Auth Setup):

```
run js mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"
```

**Expected Result:**
- ✅ Runs using your existing Draftr session
- ✅ Changes link
- ✅ Clicks Save
- ✅ Returns confirmation

### For Streamlit Cloud Later:

1. **Test locally first** to verify it works
2. **Choose authentication method** (cookies recommended)
3. **Add auth step** to MDC file
4. **Store credentials** in Streamlit Secrets
5. **Test on cloud**

---

## 📚 Resources

**Playwright Authentication:**
- https://playwright.dev/docs/auth

**Streamlit Secrets:**
- https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

**Cookie Management:**
- https://playwright.dev/docs/api/class-browsercontext#browser-context-add-cookies

---

## ✅ Summary

**How authentication works:**
- **Local:** Uses your existing browser session ✅ (works now!)
- **Cloud:** Needs cookies or login step ⚠️ (requires setup)

**What you need to do:**
- **For local testing:** Nothing! Just run it.
- **For Streamlit Cloud:** Add cookies to Streamlit Secrets (5 minutes)

**The MDC file is ready** - authentication is the only piece left for cloud deployment!

