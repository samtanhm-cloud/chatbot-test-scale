# Draftr Authentication Guide

## 🚨 The Problem

Your automation is failing because **Draftr requires login**, but headless browsers don't have your session.

**Evidence:**
- ✅ Navigation to Draftr URL works
- ❌ Screenshots show blank/login page
- ❌ JavaScript returns `undefined` (page has no content)

---

## 🎯 Solutions (Ranked by Ease)

### **Option 1: Test Locally with Visible Browser** ⭐ **EASIEST FOR TESTING**

This lets you see what's happening and manually log in:

**Step 1:** Temporarily change config for local testing:
```bash
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

# Backup original
cp playwright-mcp-config.json playwright-mcp-config.json.backup

# Use local config
cp playwright-mcp-config-local.json playwright-mcp-config.json
```

**Step 2:** Run your test:
```bash
node mdc_executor.js mdc_files/draftr-save-test.mdc --context '{"variables":{"asset_id":"3934720"}}'
```

**You will see:**
- 🖥️ A real browser window opens
- 🔐 Draftr login page (if not logged in)
- 👀 You can manually log in
- 📊 See exactly what the automation does

**Step 3:** Restore headless config:
```bash
# Restore original (for Streamlit Cloud)
mv playwright-mcp-config.json.backup playwright-mcp-config.json
```

---

### **Option 2: Use Stored Authentication (Browser Profile)**

Save your logged-in browser session and reuse it:

**Not yet implemented** - Would require:
1. Save your browser cookies/session after logging into Draftr
2. Load those cookies in the automation before navigating
3. Store cookies as environment variables in Streamlit Cloud

---

### **Option 3: Add Login Step to MDC Files**

Add authentication directly in the automation:

**Challenges:**
- Draftr likely uses **SSO/SAML** (complex authentication flow)
- May require 2FA (can't be automated easily)
- API tokens might be better if available

**Would require:**
1. Knowing Draftr's authentication method
2. Adding login steps at the start of each MDC file
3. Storing credentials securely

---

### **Option 4: Use Draftr API Instead** ⭐ **BEST FOR PRODUCTION**

If Draftr has an API, use that instead of browser automation:

**Advantages:**
- ✅ No browser needed
- ✅ Faster and more reliable
- ✅ Works in any environment
- ✅ Easier authentication (API tokens)

**Check if Draftr has:**
- REST API for link updates
- API tokens or service accounts
- Developer documentation

---

## 🧪 **Recommended Testing Path**

### **For Local Development:**

1. **Use Option 1** (visible browser) to test
2. Log in manually when the browser opens
3. Watch the automation run and see what happens
4. Debug any issues visually

### **For Streamlit Cloud:**

You **MUST** add authentication because:
- Headless mode is required (no display)
- No manual login possible
- Need automated authentication

**Recommended approach:**
1. **Check if Draftr has an API** - this is the best solution
2. If no API, use stored session cookies (Option 2)
3. Last resort: Add login automation (Option 3) - complex with SSO

---

## 📝 **What You Need to Find Out**

Ask your Draftr admin/team:

1. **Does Draftr have a REST API?**
   - For updating links programmatically
   - With API key/token authentication

2. **What authentication method does Draftr use?**
   - SSO/SAML?
   - Username/password?
   - 2FA?

3. **Can you create a service account?**
   - Dedicated account for automation
   - No 2FA requirement
   - API token access

---

## 🚀 **Quick Test: Run Locally Now**

Try this to see the actual login page:

```bash
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

# Use the local non-headless config
cp playwright-mcp-config-local.json playwright-mcp-config.json

# Run test
node mdc_executor.js mdc_files/draftr-save-test.mdc --context '{"variables":{"asset_id":"3934720"}}'

# Watch the browser window open!
# You'll see the actual Draftr login page
# Try logging in manually while the automation runs

# Restore original when done
git checkout playwright-mcp-config.json
```

This will show you:
- ✅ What authentication Draftr uses
- ✅ What the login flow looks like
- ✅ Whether automation is even possible

---

## ⚡ **Next Steps**

1. **Run the local test** (see above) to see what authentication method Draftr uses
2. **Take a screenshot** of the login page
3. **Report back** with:
   - What you see when browser opens
   - What authentication method it uses
   - Whether you have API access

Then we can implement the right authentication solution! 🎯

