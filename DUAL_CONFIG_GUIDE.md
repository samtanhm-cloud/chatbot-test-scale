# 🔄 Dual Configuration Guide

Your app now **automatically detects** whether it's running locally or on cloud and uses the appropriate browser settings!

---

## 🌍 How It Works

### Auto-Detection Logic:
```javascript
const isLocal = !this.isCloud && process.env.STREAMLIT_RUNTIME_ENV !== 'cloud';
```

**Checks:**
1. Is `/mount/src` present? (Cloud indicator)
2. Is `STREAMLIT_RUNTIME_ENV` set to 'cloud'?
3. If NO to both → **LOCAL mode**
4. If YES to either → **CLOUD mode**

---

## 🏠 LOCAL Mode (Your Mac)

### Settings:
- ✅ **Browser:** Chrome (visible window)
- ✅ **Headless:** `false` (you can see the browser)
- ✅ **Timeout:** 3 minutes (180 seconds)
- ✅ **Manual Login:** You have time to log in
- ✅ **Use Case:** Testing, debugging, manual workflows

### What You'll See:
```
[MCP Server] ==========================================
[MCP Server] Environment: 🏠 LOCAL
[MCP Server] ==========================================
[MCP Server]   Browser Mode: 👁️  VISIBLE (3-min manual login)
[MCP Server]   PLAYWRIGHT_HEADLESS: 0 (visible)
```

### Testing Locally:
```
Prompt: Check asset 3934720 in Draftr
```
1. Chrome window opens (visible!)
2. You see the Draftr page
3. **You have 3 minutes to manually log in**
4. Automation continues after you log in
5. Results appear in Streamlit

---

## ☁️ CLOUD Mode (Streamlit Cloud)

### Settings:
- ✅ **Browser:** Chrome (headless)
- ✅ **Headless:** `true` (no GUI)
- ✅ **Timeout:** 30 seconds (standard)
- ✅ **Authentication:** Automated (uses saved session)
- ✅ **Use Case:** Production, automated workflows

### What Gets Logged:
```
[MCP Server] ==========================================
[MCP Server] Environment: ☁️  CLOUD
[MCP Server] ==========================================
[MCP Server]   Browser Mode: 🔒 HEADLESS (automated)
[MCP Server]   PLAYWRIGHT_HEADLESS: 1 (headless)
```

### Cloud Deployment:
```
Same prompt: Check asset 3934720 in Draftr
```
1. Chrome runs in headless mode (no window)
2. Loads saved authentication automatically
3. Executes automation
4. Returns results

---

## 📋 Configuration Files

### Main Config (`playwright-mcp-config.json`)
- Used as template
- Contains comments explaining modes
- Gets overridden by `mdc_executor.js`

### Local Config (`playwright-mcp-config-local.json`)
- Visible browser
- 3-minute timeouts
- Manual login support

### Cloud Config (`playwright-mcp-config-cloud.json`)
- Headless browser
- Standard timeouts
- Automated authentication

---

## 🔧 Environment Variables Set Automatically

### Local Mode:
```javascript
PLAYWRIGHT_HEADLESS: '0'        // Visible
BROWSER_HEADLESS: 'false'
HEADLESS: 'false'
CHROME_HEADLESS: 'false'
DISABLE_GPU: 'false'
```

### Cloud Mode:
```javascript
PLAYWRIGHT_HEADLESS: '1'        // Headless
BROWSER_HEADLESS: 'true'
HEADLESS: 'true'
CHROME_HEADLESS: 'true'
DISABLE_GPU: 'true'
```

---

## 🎯 Usage Examples

### Local Testing (Visible Browser):
```bash
# On your Mac
cd streamlit_mdc_app
streamlit run app.py

# Enter prompt:
Check asset 3934720 in Draftr

# Browser opens (visible) → You log in manually → Automation continues
```

### Cloud Deployment (Headless):
```bash
# Push to GitHub
git push

# Streamlit Cloud automatically:
# - Detects cloud environment
# - Runs in headless mode
# - Uses saved authentication
# - Executes automation
```

---

## 🔐 Cloud Authentication Setup

Since cloud can't show a visible browser, you need to set up authentication:

### Option 1: Capture Session Locally, Upload to Cloud ⭐ RECOMMENDED

**Step 1: Capture locally**
```bash
cd streamlit_mdc_app
node setup_draftr_auth.js
# Log in when Chrome opens
# Session saved to: auth/draftr-session.json
```

**Step 2: Encode for Streamlit secrets**
```bash
cat auth/draftr-session.json | base64 > session-base64.txt
```

**Step 3: Add to Streamlit Cloud**
1. Go to your app on Streamlit Cloud
2. Click Settings → Secrets
3. Add:
```toml
DRAFTR_SESSION_BASE64 = "paste_base64_content_here"
```

**Step 4: Decode in app** (already in `app.py`)
```python
if 'DRAFTR_SESSION_BASE64' in st.secrets:
    session_data = base64.b64decode(st.secrets['DRAFTR_SESSION_BASE64'])
    os.makedirs('auth', exist_ok=True)
    with open('auth/draftr-session.json', 'wb') as f:
        f.write(session_data)
```

---

## ✅ Verification

### Check Which Mode is Active:

Look for this in the logs:

**Local:**
```
🌍 Environment: LOCAL (visible browser)
👁️  VISIBLE (3-min manual login)
```

**Cloud:**
```
🌍 Environment: CLOUD (headless)
🔒 HEADLESS (automated)
```

---

## 🐛 Troubleshooting

### Issue: Cloud still tries to open visible browser

**Check:**
```bash
# In cloud logs, should see:
[MCP Server] Environment: ☁️  CLOUD
PLAYWRIGHT_HEADLESS: 1
```

**Fix:** Environment detection might be failing. Check:
- Is `STREAMLIT_RUNTIME_ENV` set?
- Is `/mount/src` present?

### Issue: Local mode not showing browser

**Check logs:**
```bash
# Should see:
[MCP Server] Environment: 🏠 LOCAL
PLAYWRIGHT_HEADLESS: 0
```

**Fix:** Make sure you're NOT on Streamlit Cloud

### Issue: Authentication fails on cloud

**Solution:** Set up saved session (see Cloud Authentication Setup above)

---

## 📊 Comparison

| Feature | Local Mode | Cloud Mode |
|---------|-----------|------------|
| **Browser** | Visible Chrome | Headless Chrome |
| **Login** | Manual (3 minutes) | Automated (saved session) |
| **Timeout** | 180 seconds | 30 seconds |
| **Use Case** | Testing, debugging | Production, automation |
| **User Interaction** | ✅ Allowed | ❌ Not possible |
| **Authentication** | Manual login | Saved session/tokens |
| **Speed** | Slower (wait for login) | Fast (automated) |

---

## 🎉 Benefits

### ✅ Best of Both Worlds:
1. **Local:** See what's happening, debug issues, manual control
2. **Cloud:** Automated, fast, production-ready
3. **No manual switching:** Detects environment automatically
4. **Same codebase:** Works everywhere without changes
5. **Secure:** No credentials in code

---

## 🚀 Next Steps

### For Local Testing:
```bash
streamlit run app.py
# Test prompt: Check asset 3934720 in Draftr
# Browser opens → Log in → Works!
```

### For Cloud Deployment:
1. Set up authentication (capture session locally)
2. Upload session to Streamlit secrets
3. Push code to GitHub
4. Streamlit Cloud handles the rest!

---

## 📝 Summary

✅ **Automatic detection** - No manual configuration needed  
✅ **Local mode** - Visible browser, 3-min manual login  
✅ **Cloud mode** - Headless, automated authentication  
✅ **Same prompts** - Work in both environments  
✅ **Secure** - No credentials in code  
✅ **Chrome everywhere** - Consistent browser

**Your app is now production-ready for both local testing and cloud deployment!** 🎉

