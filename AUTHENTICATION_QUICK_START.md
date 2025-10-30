# 🚀 Authentication Quick Start - Choose Your Method

**Pick the best authentication method for your use case!**

---

## 🎯 **TLDR - Which Should You Use?**

```
Local Development:
  → Persistent Session ⭐⭐⭐⭐⭐
    Run: node setup_draftr_auth.js

Streamlit Cloud:
  → IDSDK OAuth ⭐⭐⭐⭐
    Run: python3 autodesk_idsdk_login.py

Quick Test:
  → Session Cookies ⭐⭐
    Run: node capture-cookies.js
```

---

## 🏆 **Method 1: Persistent Browser Session (BEST FOR LOCAL!)**

### **What It Is:**
Log in once in a browser, session saved forever. NO secrets needed!

### **Setup (2 minutes):**
```bash
node setup_draftr_auth.js
# Browser opens → Log in → Press ENTER → Done!
```

### **Pros:**
- ✅ **SIMPLEST** - Just log in like normal!
- ✅ **No secrets** - File on disk
- ✅ **SSO/2FA automatic** - Real login flow
- ✅ **Long-lived** - 30+ days
- ✅ **2 minute setup** - ONE TIME!

### **Cons:**
- ⚠️ Local only (can't do interactive login on cloud)

### **When to Use:**
- ✅ Local development
- ✅ Personal use
- ✅ Maximum simplicity

### **Full Guide:**
→ `PERSISTENT_SESSION_GUIDE.md`

---

## 🔐 **Method 2: IDSDK OAuth Token (BEST FOR CLOUD!)**

### **What It Is:**
Official Autodesk OAuth 2.0 authentication. Token auto-refreshes!

### **Setup (10 minutes ONE TIME):**
```bash
# 1. Get Client ID from https://aps.autodesk.com/
# 2. Add to secrets:
echo 'AUTODESK_CLIENT_ID = "your_id"' >> .streamlit/secrets.toml

# 3. Run login:
python3 autodesk_idsdk_login.py

# 4. Copy token output to secrets
# 5. Done!
```

### **Pros:**
- ✅ **Most secure** - OAuth 2.0 standard
- ✅ **Auto-refresh** - No manual work
- ✅ **SSO/2FA** - Handled during login
- ✅ **Cloud-ready** - Works on Streamlit Cloud
- ✅ **Audit trail** - Complete logging

### **Cons:**
- ⚠️ Requires Autodesk app credentials
- ⚠️ Slightly more complex setup

### **When to Use:**
- ✅ Streamlit Cloud deployment
- ✅ CI/CD pipelines
- ✅ Production environments
- ✅ Multiple users

### **Full Guide:**
→ `AUTODESK_IDSDK_GUIDE.md`

---

## 🍪 **Method 3: Session Cookies (LAST RESORT)**

### **What It Is:**
Manually capture cookies from logged-in browser.

### **Setup (5 minutes, repeat every 1-2 hours):**
```bash
node capture-cookies.js
# Browser opens → Log in → Press ENTER
# Copy output to secrets
```

### **Pros:**
- ✅ Works right now (no approvals needed)
- ✅ Quick to test

### **Cons:**
- ❌ **Short-lived** - Expires every 1-2 hours
- ❌ **Manual recapture** - Every time expires
- ❌ **Less secure** - Session hijacking risk
- ❌ **Slow** - 5-10 seconds overhead

### **When to Use:**
- ⚠️ Last resort only
- ⚠️ Quick proof of concept
- ⚠️ Can't get other methods approved

### **Full Guide:**
→ `COOKIE_AUTH_SETUP.md`

---

## 📊 **Side-by-Side Comparison:**

| Feature | Persistent Session | IDSDK OAuth | Cookies |
|---------|-------------------|-------------|---------|
| **Setup Time** | 2 min | 10 min | 5 min |
| **Frequency** | ONE TIME (30+ days) | ONE TIME (forever) | Every 1-2 hours |
| **Secrets Needed** | ❌ NO | ✅ Yes | ✅ Yes |
| **SSO/2FA** | ✅ Perfect | ✅ Good | ⚠️ Manual |
| **Cloud Deploy** | ❌ No | ✅ Yes | ✅ Yes |
| **Local Dev** | ✅✅✅ Perfect | ✅ Good | ✅ OK |
| **Security** | ✅ High | ✅ Highest | ⚠️ Medium |
| **Maintenance** | None (30+ days) | None | Hourly |
| **Complexity** | Super simple | Medium | Medium |
| **Speed** | <1s | <1s | 5-10s |

---

## 🎯 **Decision Tree:**

```
Are you deploying to Streamlit Cloud?
│
├─ YES → Use IDSDK OAuth ⭐⭐⭐⭐
│         (Best for cloud, auto-refresh, secure)
│         Run: python3 autodesk_idsdk_login.py
│
└─ NO (Local development)
   │
   ├─ Want SIMPLEST method?
   │  └─ YES → Use Persistent Session ⭐⭐⭐⭐⭐
   │           (Just log in once!)
   │           Run: node setup_draftr_auth.js
   │
   └─ Need quick test?
      └─ YES → Use Cookies ⭐⭐
               (Works but requires maintenance)
               Run: node capture-cookies.js
```

---

## 🚀 **Quick Start Commands:**

### **For Local Development (RECOMMENDED):**
```bash
# Simplest method - just log in once!
node setup_draftr_auth.js
```

### **For Streamlit Cloud:**
```bash
# Get Autodesk Client ID first, then:
python3 autodesk_idsdk_login.py
```

### **For Quick Test:**
```bash
# Works but expires quickly
node capture-cookies.js
```

---

## 📝 **Setup Steps by Method:**

### **Persistent Session (Local):**
1. Run: `node setup_draftr_auth.js`
2. Browser opens
3. Log in to Draftr
4. Press ENTER
5. ✅ Done! Session saved for 30+ days

### **IDSDK OAuth (Cloud):**
1. Get Client ID from https://aps.autodesk.com/
2. Add to `.streamlit/secrets.toml`
3. Run: `python3 autodesk_idsdk_login.py`
4. Browser opens, log in
5. Copy token output to secrets
6. ✅ Done! Token auto-refreshes

### **Cookies (Fallback):**
1. Run: `node capture-cookies.js`
2. Browser opens, log in
3. Press ENTER
4. Copy output to secrets
5. ⚠️ Repeat every 1-2 hours

---

## 💡 **Recommendations:**

### **If You're Starting Fresh:**

**Local development:**
```bash
# Use Persistent Session (simplest!)
node setup_draftr_auth.js
```

**Deploying to cloud:**
```bash
# Use IDSDK OAuth (most robust)
python3 autodesk_idsdk_login.py
```

### **If You're Currently Using Cookies:**

**Upgrade to Persistent Session (local):**
```bash
# Much simpler!
node setup_draftr_auth.js
# Delete old capture-cookies.js
# Remove DRAFTR_COOKIES from secrets
```

**Or Upgrade to IDSDK (cloud):**
```bash
# More secure!
python3 autodesk_idsdk_login.py
# Keep cookies as fallback if needed
```

---

## ⚡ **Performance:**

### **Setup Time:**
- Persistent Session: **2 min** ⚡⚡⚡
- IDSDK OAuth: **10 min** ⚡⚡
- Cookies: **5 min** (but EVERY 1-2 hours!) ⚡

### **Runtime Speed:**
- Persistent Session: **<1 second** ⚡⚡⚡
- IDSDK OAuth: **<1 second** ⚡⚡⚡
- Cookies: **5-10 seconds** ⚡

### **Maintenance:**
- Persistent Session: **None for 30+ days** 🎉
- IDSDK OAuth: **None (auto-refresh)** 🎉
- Cookies: **Every 1-2 hours** 😫

---

## 📚 **Full Documentation:**

- **Persistent Session:** `PERSISTENT_SESSION_GUIDE.md` ⭐ NEW! Simplest!
- **IDSDK OAuth:** `AUTODESK_IDSDK_GUIDE.md` ⭐ Best for cloud
- **Session Cookies:** `COOKIE_AUTH_SETUP.md` ⚠️ Last resort
- **All Methods Compared:** `AUTHENTICATION_COMPARISON.md`

---

## 🎯 **What to Do RIGHT NOW:**

### **Choice A: Local Development (Simplest)**
```bash
cd streamlit_mdc_app
node setup_draftr_auth.js
# Just log in once - that's it! ✨
```

### **Choice B: Cloud Deployment (Most Robust)**
```bash
cd streamlit_mdc_app
python3 autodesk_idsdk_login.py
# Get token, add to secrets ✨
```

### **Choice C: Quick Test (Works But Not Ideal)**
```bash
cd streamlit_mdc_app
node capture-cookies.js
# Capture cookies (but will expire soon) ⚠️
```

---

## ✅ **Success Checklist:**

After setup, verify authentication works:

```bash
# Start Streamlit
streamlit run app.py

# Check for one of these messages:
# ✅ "🔐 Authentication: Persistent Browser Session"
# ✅ "🔐 Authentication: IDSDK OAuth Token"
# ✅ "🔐 Authentication: Session Cookies"

# Run test automation
# Enter: "Update link in asset 3934720"
# Should work without login prompt!
```

---

## 🎉 **Congratulations!**

You now have **3 authentication options**:

1. **Persistent Session** - Simplest (local)
2. **IDSDK OAuth** - Most robust (cloud)
3. **Session Cookies** - Fallback (works anywhere)

**Pick the one that fits your needs and start automating!** 🚀

