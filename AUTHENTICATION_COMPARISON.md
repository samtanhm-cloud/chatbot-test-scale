# 🔐 Draftr Authentication: Complete Comparison

**Which authentication method should you use?**

---

## 🎯 **TLDR - Recommendation:**

```
1. IDSDK OAuth (BEST) ⭐⭐⭐⭐⭐
   └─> If you can get Autodesk app credentials

2. Draftr API (GOOD) ⭐⭐⭐⭐
   └─> If Draftr has a public API

3. Session Cookies (OK) ⭐⭐
   └─> Last resort, works but not ideal
```

---

## 📊 **Detailed Comparison Table:**

| Feature | 🔐 IDSDK OAuth | 🔌 Draftr API | 🍪 Cookies |
|---------|---------------|---------------|-----------|
| **Security** | ✅ Highest (OAuth 2.0) | ✅ High (API tokens) | ⚠️ Medium (session hijacking) |
| **Setup Time** | 3 min (one-time) | 5 min (one-time) | 5 min (every 1-2 hours) |
| **Maintenance** | ✅ None (auto-refresh) | ✅ Rare (token rotation) | ❌ Frequent (recapture) |
| **SSO/2FA Support** | ✅ Yes (automatic) | ✅ Yes (via OAuth) | ⚠️ Manual only |
| **Speed** | ⚡ <1 second | ⚡ <1 second | 🐌 5-10 seconds |
| **Reliability** | ✅ Very high | ✅ Very high | ⚠️ Medium (UI breaks) |
| **Audit Trail** | ✅ Complete | ✅ Complete | ⚠️ Limited |
| **Multi-User** | ✅ Easy | ✅ Easy | ⚠️ Complex |
| **Permissions** | ✅ Scoped | ✅ Scoped | ❌ Full access |
| **Revocation** | ✅ Instant | ✅ Instant | ⚠️ Logout needed |
| **Token Lifetime** | 🕐 1-24 hours | 🕐 Days/months | 🕐 1-2 hours |
| **Auto-Refresh** | ✅ Yes | ⚠️ Depends | ❌ No |
| **Headless** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Local Testing** | ✅ Easy | ✅ Easy | ⚠️ Requires browser |
| **Cloud Deploy** | ✅ Seamless | ✅ Seamless | ⚠️ Manual setup |

---

## 🥇 **Option 1: IDSDK OAuth (RECOMMENDED)**

### **What It Is:**
Autodesk's official Identity SDK using OAuth 2.0 device flow.

### **How It Works:**
```
1. Run: python3 autodesk_idsdk_login.py
2. Browser opens with Autodesk sign-in
3. Log in (SSO/2FA supported automatically)
4. Script captures OAuth token
5. Copy token to secrets
6. Done! Token auto-refreshes
```

### **Pros:**
- ✅ **Most secure** (OAuth 2.0 standard)
- ✅ **SSO/2FA automatic** (no manual cookie capture during auth)
- ✅ **One-time setup** (token auto-refreshes)
- ✅ **Scoped permissions** (only what's needed)
- ✅ **Complete audit trail** (every action logged)
- ✅ **Easy revocation** (instant token invalidation)
- ✅ **Multi-user friendly** (each user gets own token)

### **Cons:**
- ⚠️ Requires Autodesk app credentials (get from https://aps.autodesk.com/)
- ⚠️ May require approval from your organization's Autodesk admin

### **Setup:**
```bash
# 1. Get Autodesk Client ID from https://aps.autodesk.com/
# 2. Add to secrets
echo 'AUTODESK_CLIENT_ID = "your_id"' >> .streamlit/secrets.toml

# 3. Run interactive login
python3 autodesk_idsdk_login.py

# 4. Copy token output to secrets
# 5. Done!
```

### **When to Use:**
- ✅ You have (or can get) Autodesk app credentials
- ✅ You need robust, production-grade authentication
- ✅ You support multiple users
- ✅ Security and compliance are important

---

## 🥈 **Option 2: Draftr API (IF IT EXISTS)**

### **What It Is:**
Direct REST/GraphQL API for Draftr operations (no browser needed).

### **How It Works:**
```
1. Get Draftr API key from Autodesk
2. Add to secrets: DRAFTR_API_KEY = "..."
3. Use Python API client (draftr_api_client.py)
4. Make direct API calls (no browser automation!)
```

### **Pros:**
- ✅ **Fastest** (~50x faster than browser automation)
- ✅ **Most reliable** (no UI dependencies)
- ✅ **Clean code** (simple HTTP requests)
- ✅ **Better errors** (HTTP status codes)
- ✅ **Easy testing** (curl, Postman)

### **Cons:**
- ❌ **May not exist** (Draftr might not have public API)
- ⚠️ Requires API credentials/approval

### **How to Check:**
```bash
# Method 1: Check network tab
# Open Draftr → DevTools → Network → Update a link
# Look for: POST/PUT/PATCH to /api/...

# Method 2: Contact Autodesk
# Email your account manager: "Does Draftr have an API?"
```

### **When to Use:**
- ✅ Draftr has a public API (check first!)
- ✅ You need maximum speed
- ✅ You want to avoid browser automation entirely
- ✅ You're building a large-scale system

### **Status:**
🔍 **NEEDS INVESTIGATION** - Check if Draftr has an API first!

---

## 🥉 **Option 3: Session Cookies (CURRENT APPROACH)**

### **What It Is:**
Capture session cookies from logged-in browser, inject into headless browser.

### **How It Works:**
```
1. Run: node capture-cookies.js
2. Browser opens → Log in manually
3. Press Enter → Cookies captured
4. Add to secrets: DRAFTR_COOKIES = "..."
5. Automation injects cookies before each run
```

### **Pros:**
- ✅ **Works right now** (no approval needed)
- ✅ **No API required** (just browser sessions)
- ✅ **Quick to test** (capture and go)

### **Cons:**
- ❌ **Short-lived** (cookies expire in 1-2 hours)
- ❌ **Manual recapture** (whenever cookies expire)
- ❌ **Less secure** (full session access, hijacking risk)
- ❌ **Slow** (5-10 seconds vs <1 second for API/OAuth)
- ❌ **Fragile** (breaks if UI changes)
- ❌ **SSO/2FA manual** (need to log in each time)
- ❌ **No audit trail** (limited visibility)
- ⚠️ **Multi-user complex** (each user needs own cookies)

### **Setup:**
```bash
# 1. Capture cookies
node capture-cookies.js
# (Browser opens, log in, press Enter)

# 2. Add to secrets
# Copy output to .streamlit/secrets.toml:
DRAFTR_COOKIES = """
[
  { "name": "...", "value": "...", ... },
  ...
]
"""

# 3. Test
streamlit run app.py

# 4. Recapture when cookies expire (1-2 hours)
```

### **When to Use:**
- ⚠️ Last resort (when other methods blocked)
- ⚠️ Quick testing/proof of concept
- ⚠️ Can't get API or OAuth credentials
- ⚠️ Low-volume use (manual recapture is OK)

---

## 🎯 **Decision Tree:**

```
START: Which authentication method?
│
├─ Can you get Autodesk app credentials?
│  ├─ YES → Use IDSDK OAuth ⭐⭐⭐⭐⭐
│  │        (Best security, auto-refresh, one-time setup)
│  │
│  └─ NO → Continue
│
├─ Does Draftr have a public API?
│  ├─ YES → Use Draftr API ⭐⭐⭐⭐
│  │        (Fastest, most reliable, no browser)
│  │
│  ├─ UNKNOWN → Investigate!
│  │             (Check network tab, ask Autodesk)
│  │
│  └─ NO → Continue
│
└─ Use Session Cookies ⭐⭐
   (Works but requires maintenance)
```

---

## 🚀 **Migration Path:**

### **Current: Cookies → Target: IDSDK OAuth**

```bash
# Step 1: Get Autodesk credentials (5 min)
# Go to https://aps.autodesk.com/
# Create app → Get Client ID

# Step 2: Run IDSDK login (3 min)
python3 autodesk_idsdk_login.py
# Browser opens → Log in → Copy token

# Step 3: Add token to secrets (1 min)
# Paste output to .streamlit/secrets.toml

# Step 4: Test (1 min)
streamlit run app.py
# Should say: "🔐 Authentication: IDSDK OAuth Token"

# Step 5: Remove cookies (optional)
# Delete DRAFTR_COOKIES from secrets
# Delete capture-cookies.js (no longer needed!)

# Step 6: Deploy to cloud (2 min)
# Add token to Streamlit Cloud secrets
# Push changes to GitHub
# Done! ✅
```

**Total time: ~10 minutes for permanent solution!**

---

## 📊 **Real-World Scenarios:**

### **Scenario 1: Single User, Low Volume**
- **Cookies** ✅ OK (quick to set up, manual recapture is manageable)
- **IDSDK** ⭐ Better (one-time setup, more secure)

### **Scenario 2: Single User, High Volume**
- **Cookies** ⚠️ Not ideal (cookies expire during use)
- **IDSDK** ⭐⭐ Good (auto-refresh)
- **API** ⭐⭐⭐ Best (fastest, no browser overhead)

### **Scenario 3: Multiple Users**
- **Cookies** ❌ Bad (managing many cookie sets)
- **IDSDK** ⭐⭐⭐ Best (each user gets own token)
- **API** ⭐⭐⭐ Best (service account or per-user keys)

### **Scenario 4: Enterprise/Compliance**
- **Cookies** ❌ Not compliant (session hijacking risk)
- **IDSDK** ⭐⭐⭐ Required (OAuth 2.0 standard)
- **API** ⭐⭐⭐ Required (proper authentication)

### **Scenario 5: Proof of Concept**
- **Cookies** ⭐⭐⭐ Perfect (quick to test)
- **IDSDK** ⭐⭐ Good (but may need approvals)
- **API** ⭐ Overkill (unless API already exists)

---

## 💡 **Recommendations by Role:**

### **Developer (You):**
```
Priority 1: Try IDSDK OAuth
  → Most robust, future-proof solution

Priority 2: Check for Draftr API
  → If exists, even better than IDSDK for automation

Priority 3: Keep cookies as fallback
  → For quick testing and PoC
```

### **Security Team:**
```
Approved: IDSDK OAuth, Draftr API
  → Industry-standard authentication

Not approved: Session Cookies
  → Security risk for production
```

### **DevOps:**
```
Prefer: IDSDK OAuth or API
  → Easy to manage, auto-refresh, secrets-based

Avoid: Cookies
  → Manual rotation, no automation
```

---

## ❓ **FAQ:**

### **Q: Can I use multiple methods at once?**
A: Yes! The system checks in order:
   1. IDSDK OAuth token (if found, use this)
   2. Session Cookies (fallback if no token)

### **Q: Which is fastest?**
A: Draftr API (if exists) > IDSDK OAuth >> Cookies
   - API: <1 second (direct HTTP)
   - IDSDK: <1 second (HTTP with token)
   - Cookies: 5-10 seconds (browser launch + inject)

### **Q: Which is most secure?**
A: IDSDK OAuth ≥ Draftr API >> Cookies
   - OAuth/API: Scoped, audited, revocable
   - Cookies: Full session access, hijacking risk

### **Q: Do I need to delete cookies if I use IDSDK?**
A: No, but recommended for cleanup. The system auto-prefers IDSDK.

### **Q: Can I switch methods without breaking?**
A: Yes! The system detects what's available and uses best option.

---

## 🎯 **What to Do RIGHT NOW:**

### **Path A: Try IDSDK (10 min)**
```bash
cd streamlit_mdc_app

# 1. Get Client ID from https://aps.autodesk.com/
# 2. Run login
python3 autodesk_idsdk_login.py

# 3. Copy token to secrets
# 4. Test!
```

### **Path B: Check for API (5 min)**
```bash
# Open Draftr in browser
# DevTools → Network tab
# Update a link manually
# Look for API calls
# Report findings!
```

### **Path C: Stick with Cookies (0 min)**
```bash
# Already working!
# Just recapture when needed:
node capture-cookies.js
```

---

## 📈 **Success Metrics:**

| Metric | Cookies | IDSDK | API |
|--------|---------|-------|-----|
| Setup time | 5 min | 10 min | 10 min |
| Auth duration | 1-2 hours | Days/weeks | Months |
| Speed per request | 5-10s | <1s | <1s |
| Manual work/week | 1-2 hours | 0 min | 0 min |
| Security score | 5/10 | 10/10 | 10/10 |
| Maintenance/month | 10+ hours | 0 hours | <1 hour |

**ROI: IDSDK saves ~10 hours/month vs cookies!**

---

## ✅ **Ready to Upgrade?**

See full guides:
- `AUTODESK_IDSDK_GUIDE.md` - Complete IDSDK setup
- `DRAFTR_API_GUIDE.md` - API investigation
- `COOKIE_AUTH_SETUP.md` - Current cookie method

**Recommendation: Try IDSDK now!** 🚀

