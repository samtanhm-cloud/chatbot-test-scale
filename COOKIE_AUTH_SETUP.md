# 🔐 Cookie-Based Authentication Setup Guide

Complete guide to set up authentication for Draftr automation using session cookies.

---

## 🎯 **Overview**

This method lets you:
- ✅ **Log in once manually** (with SSO/2FA)
- ✅ **Capture session cookies**
- ✅ **Store them securely** in Streamlit secrets
- ✅ **Reuse them** for automated access
- ✅ **Works on Streamlit Cloud** (headless mode)

---

## 📋 **Setup Steps**

### **Step 1: Capture Your Cookies (Local)**

Run the cookie capture script:

```bash
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

# Install Playwright if not already done
npm install

# Run the cookie capture script
node capture-cookies.js
```

**What happens:**
1. ✅ Browser window opens
2. ✅ Navigate to Draftr and log in manually (use SSO/2FA as normal)
3. ✅ Wait until you see the Draftr homepage
4. ✅ Press ENTER in terminal
5. ✅ Script captures cookies and outputs them

**You will see output like:**

```
============================================================
📋 COPY THIS TO YOUR STREAMLIT SECRETS:
============================================================

# Draftr Authentication Cookies
DRAFTR_COOKIES = """
[
  {
    "name": "session_id",
    "value": "abc123...",
    "domain": ".autodesk.com",
    "path": "/",
    "secure": true,
    "sameSite": "None"
  },
  ...more cookies...
]
"""
```

---

### **Step 2: Add Cookies to Streamlit Secrets**

#### **For Local Development:**

Create/edit: `.streamlit/secrets.toml`

```toml
# Draftr Authentication Cookies
DRAFTR_COOKIES = """
[
  {
    "name": "session_id",
    "value": "abc123...",
    "domain": ".autodesk.com",
    "path": "/",
    "secure": true,
    "sameSite": "None"
  }
]
"""
```

#### **For Streamlit Cloud:**

1. Go to your app: https://share.streamlit.io/
2. Click your app → **⚙️ Settings**
3. Click **Secrets** tab
4. Paste the exact output from Step 1:

```toml
DRAFTR_COOKIES = """
[
  {
    "name": "session_id",
    "value": "abc123...",
    ...
  }
]
"""
```

5. Click **Save**

---

### **Step 3: Test the Authentication**

#### **Test Locally:**

```bash
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

# Make sure headless mode is enabled
git checkout playwright-mcp-config.json

# Run your Streamlit app
streamlit run app.py
```

#### **Test on Streamlit Cloud:**

1. Push changes to GitHub:
```bash
git add -A
git commit -m "Add cookie-based authentication"
git push origin main
```

2. Wait for Streamlit Cloud to redeploy
3. Try running a Draftr automation
4. Check the execution logs for:
   - `🔐 Loading authentication cookies from secrets...`
   - `✅ Loaded X cookies for authentication`
   - `[MDC Executor] Injecting X authentication cookies...`
   - `[MDC Executor] ✅ Cookies injected successfully`

---

## 🔄 **How It Works**

### **Flow:**

1. **User triggers automation** in Streamlit
2. **`app.py` checks secrets** for `DRAFTR_COOKIES`
3. **Cookies are loaded** and parsed from JSON
4. **Cookies passed to `mdc_executor.js`** via context
5. **Before navigation**, cookies are injected into browser
6. **Browser is now authenticated** as you!
7. **Automation runs** with your session

### **Code Flow:**

```
app.py (line 538-544)
  ↓ Loads cookies from secrets
  ↓ Parses JSON
  ↓ Adds to context
  ↓
mdc_executor.js (line 90-118)
  ↓ Receives cookies in context
  ↓ Navigates to base domain
  ↓ Injects cookies via JavaScript
  ↓ Continues with automation
```

---

## 🔒 **Security Best Practices**

### **DO:**
- ✅ **Store cookies ONLY in Streamlit secrets** (encrypted)
- ✅ **Use `.gitignore`** to exclude `.streamlit/secrets.toml`
- ✅ **Rotate cookies periodically** (recapture every few weeks)
- ✅ **Use a service account** if possible (no personal data)
- ✅ **Monitor access logs** in Draftr

### **DON'T:**
- ❌ **Don't commit secrets to git**
- ❌ **Don't share cookies** with others
- ❌ **Don't use personal account** cookies in production
- ❌ **Don't ignore expiration** - recapture when auth fails
- ❌ **Don't hardcode** cookies in code

---

## 🐛 **Troubleshooting**

### **Issue: "Could not load cookies from secrets"**

**Cause:** Cookies not in secrets or wrong format

**Fix:**
1. Check secrets are saved correctly
2. Ensure it's valid JSON (use JSONLint)
3. Make sure the secret name is exactly `DRAFTR_COOKIES`
4. Restart Streamlit app after adding secrets

---

### **Issue: "Cookie injection failed"**

**Cause:** Network issue or MCP server problem

**Fix:**
1. Check internet connection
2. Verify cookies are valid JSON
3. Check execution logs for detailed error
4. Try recapturing cookies

---

### **Issue: Still seeing login page**

**Cause:** Cookies expired or domain mismatch

**Fix:**
1. **Recapture cookies** - run `node capture-cookies.js` again
2. Check cookie `domain` matches Draftr domain
3. Verify cookies have `secure: true` if using HTTPS
4. Check cookie `sameSite` attribute

---

### **Issue: Authentication works locally but not on cloud**

**Cause:** Secrets not synced to cloud

**Fix:**
1. Verify secrets are added in Streamlit Cloud dashboard
2. Check for typos in secret name
3. Restart the cloud app
4. Check cloud logs for cookie loading messages

---

## ⏰ **Cookie Expiration**

**Cookies typically expire:**
- After 7-30 days of inactivity
- When you change your password
- When you explicitly log out
- When security policies change

**When cookies expire:**
1. Automation will fail with authentication errors
2. Screenshots will show login page
3. Simply **recapture cookies** and update secrets

---

## 🔄 **Recapturing Cookies (When Expired)**

```bash
# Step 1: Recapture
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"
node capture-cookies.js

# Step 2: Copy new output

# Step 3: Update secrets
# - Local: Update .streamlit/secrets.toml
# - Cloud: Update via Streamlit Cloud dashboard

# Step 4: Test
# - Local: Restart streamlit
# - Cloud: App restarts automatically after secret update
```

---

## ✅ **Verification Checklist**

Before deploying to production:

- [ ] Cookies captured successfully
- [ ] Cookies added to secrets (local and cloud)
- [ ] `.streamlit/secrets.toml` in `.gitignore`
- [ ] Headless mode enabled in `playwright-mcp-config.json`
- [ ] Test automation locally works
- [ ] Test automation on cloud works
- [ ] Execution logs show cookie injection
- [ ] Screenshots show authenticated pages (not login)

---

## 🎯 **Quick Reference**

| Task | Command |
|------|---------|
| Capture cookies | `node capture-cookies.js` |
| Test locally | `streamlit run app.py` |
| Check headless mode | `cat playwright-mcp-config.json` |
| View local secrets | `cat .streamlit/secrets.toml` |
| View cloud secrets | Streamlit Cloud → Settings → Secrets |
| Recapture expired cookies | `node capture-cookies.js` (repeat setup) |

---

## 📞 **Need Help?**

**If authentication still fails:**

1. Check execution logs for specific errors
2. Verify cookies are being loaded (look for 🔐 emoji in logs)
3. Verify cookies are being injected (look for ✅ emoji in logs)
4. Check screenshots to see what page loads
5. Try recapturing cookies with a fresh login

**Common causes:**
- Expired cookies → Recapture
- Wrong domain → Check cookie domains match Draftr
- Invalid JSON → Validate with JSONLint
- Missing secrets → Check Streamlit dashboard

---

## 🚀 **You're Ready!**

Once cookies are set up:
- ✅ Automation works in headless mode
- ✅ Works on Streamlit Cloud
- ✅ No manual login needed (until cookies expire)
- ✅ Secure (cookies encrypted in secrets)

**Run your first authenticated automation!** 🎉

