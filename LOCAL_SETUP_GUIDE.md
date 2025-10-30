# 🚀 Local Deployment - Quick Start Guide

**Get your Draftr automation running locally in 5 minutes!**

---

## ✅ **Prerequisites Check:**

Before starting, make sure you have:
- ✅ Node.js installed (v16+)
- ✅ Python 3.8+ installed
- ✅ Git (to clone/pull updates)

---

## 🎯 **Quick Start (First Time Setup):**

### **Step 1: Navigate to Project**
```bash
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"
```

### **Step 2: Install Dependencies (if needed)**

```bash
# Install Node.js packages
npm install

# Install Playwright browsers
npx playwright install chromium

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install streamlit
```

**Note:** If you've already done this, skip to Step 3!

### **Step 3: Set Up Authentication** ⭐ **IMPORTANT!**

This is the **simplest** method - just log in once!

```bash
# Run the authentication setup script
node setup_draftr_auth.js
```

**What will happen:**
1. 🌐 Browser opens automatically
2. 🔐 Navigate to Draftr login page
3. 👤 **You log in** (SSO/2FA works!)
4. ⏳ Wait for Draftr to fully load
5. ⌨️  Press ENTER in terminal
6. 💾 Session saved to `auth/draftr-session.json`
7. ✅ Done!

**Example output:**
```
🔐 Draftr Authentication Setup
========================================
Browser will open for authentication
SSO/2FA supported
No secrets to manage
========================================

🚀 Launching browser...
🌐 Navigating to Draftr...

⏸️  PLEASE LOG IN NOW
1. Complete Autodesk login
2. SSO and 2FA will work
3. Wait for Draftr to load
4. Press ENTER

💾 Saving browser session...
✅ Session saved!
📊 Cookies: 15, Domains: 3
✅ SETUP COMPLETE!
```

### **Step 4: Start Streamlit**

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start Streamlit
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### **Step 5: Open Browser & Test!**

1. Open: **http://localhost:8501**
2. You should see the Draftr automation UI
3. Try a test prompt:
   ```
   Update link "Get in touch" to "www.autodesk.com/uk/support" in asset 3934720
   ```
4. Watch it work! 🎉

---

## 🔄 **Daily Workflow (After Initial Setup):**

Once you've done the setup above, your daily workflow is super simple:

```bash
# 1. Navigate to project
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start Streamlit
streamlit run app.py

# 4. Open browser: http://localhost:8501

# 5. Use automation! ✨
```

**That's it!** No authentication steps needed daily!

---

## 🔐 **Authentication Status:**

You'll see one of these messages when you run automation:

### **✅ Authenticated (Good!):**
```
🔐 Authentication: Persistent Browser Session
✅ Using saved session from: auth/draftr-session.json
💡 Browser will already be logged in!
```

### **❌ Not Authenticated (Need to login):**
```
⚠️  No authentication configured!
💡 Run: node setup_draftr_auth.js
```

**If you see the ❌ message:**
```bash
# Just run setup again
node setup_draftr_auth.js
# Log in → Press ENTER → Done!
```

---

## 🛠️ **Troubleshooting:**

### **Problem 1: "streamlit: command not found"**

**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Or run directly
python3 -m streamlit run app.py
```

### **Problem 2: "npm: command not found"**

**Solution:**
```bash
# Install Node.js first
brew install node  # macOS
# or download from https://nodejs.org/
```

### **Problem 3: "Authentication failed" when running automation**

**Solution:**
```bash
# Session expired, re-authenticate
node setup_draftr_auth.js
# Log in again → Press ENTER
```

### **Problem 4: Browser doesn't open during setup**

**Solution:**
```bash
# Make sure Playwright is installed
npx playwright install chromium

# Try setup again
node setup_draftr_auth.js
```

### **Problem 5: "Module not found" errors**

**Solution:**
```bash
# Reinstall dependencies
npm install

# For Python packages
source venv/bin/activate
pip install streamlit
```

### **Problem 6: Port 8501 already in use**

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use different port
streamlit run app.py --server.port 8502
```

---

## 📊 **What Gets Installed:**

### **Node.js Packages:**
- `playwright` - Browser automation
- `playwright-core` - Core Playwright functionality
- `@modelcontextprotocol/sdk` - MCP integration

### **Python Packages:**
- `streamlit` - Web UI framework

### **Browsers:**
- Chromium (installed via Playwright)

### **Authentication:**
- `auth/draftr-session.json` - Your saved login session

---

## 🔍 **Verify Everything is Working:**

### **Check 1: Dependencies Installed**
```bash
# Check Node packages
npm list playwright

# Check Python packages
source venv/bin/activate
python3 -c "import streamlit; print('Streamlit:', streamlit.__version__)"

# Check browser
ls node_modules/playwright-core/.local-browsers/
```

### **Check 2: Authentication Configured**
```bash
# Check if session file exists
ls -lh auth/draftr-session.json

# If not found, run:
node setup_draftr_auth.js
```

### **Check 3: Streamlit Runs**
```bash
source venv/bin/activate
streamlit run app.py
# Should open browser to http://localhost:8501
```

### **Check 4: Automation Works**
```
1. Open Streamlit UI: http://localhost:8501
2. Enter test prompt:
   "Check authentication status"
3. Should show:
   ✅ "🔐 Authentication: Persistent Browser Session"
```

---

## 📁 **Important Files & Directories:**

```
streamlit_mdc_app/
├── app.py                      # Main Streamlit application
├── mdc_executor.js             # MDC execution engine
├── setup_draftr_auth.js        # 🔑 Run this to set up auth!
├── playwright-mcp-config.json  # Playwright configuration
│
├── auth/                       # 🔒 Your authentication
│   └── draftr-session.json     # Saved login session (created by setup)
│
├── mdc_files/                  # Automation scripts
│   ├── draftr-link-updater-js.mdc
│   └── ...
│
├── venv/                       # Python virtual environment
│   └── bin/activate            # Activate with: source venv/bin/activate
│
├── node_modules/               # Node.js packages
│   └── playwright-core/
│       └── .local-browsers/    # Chromium browser
│
└── .streamlit/
    └── secrets.toml            # (Not needed for local auth!)
```

---

## 🚀 **Quick Reference Commands:**

### **First Time Setup:**
```bash
cd streamlit_mdc_app
npm install
npx playwright install chromium
python3 -m venv venv
source venv/bin/activate
pip install streamlit
node setup_draftr_auth.js  # ⭐ Log in!
```

### **Daily Use:**
```bash
cd streamlit_mdc_app
source venv/bin/activate
streamlit run app.py
```

### **Re-authenticate (if session expires):**
```bash
node setup_draftr_auth.js
```

### **Update Code:**
```bash
git pull origin main
npm install  # If package.json changed
```

---

## 🎯 **Next Steps:**

### **After Local Setup Works:**

1. **Test different prompts:**
   ```
   Update link "Get in touch" to "new-url.com" in asset 3934720
   Replace all "/en/" links with "/uk/" in asset 3934720
   ```

2. **Learn MDC files:**
   - Check `mdc_files/` directory
   - See how automation scripts are structured

3. **Deploy to Streamlit Cloud (optional):**
   - See: `AUTODESK_IDSDK_GUIDE.md`
   - Different auth method needed for cloud

---

## 💡 **Pro Tips:**

1. **Keep session fresh:**
   ```bash
   # Session lasts 30+ days
   # If you get "login required", just re-run:
   node setup_draftr_auth.js
   ```

2. **Multiple terminal windows:**
   ```bash
   # Terminal 1: Run Streamlit
   streamlit run app.py
   
   # Terminal 2: Check logs, test scripts
   tail -f logs.txt
   ```

3. **Quick restart:**
   ```bash
   # Ctrl+C to stop Streamlit
   # Up arrow → Enter to restart
   streamlit run app.py
   ```

4. **Check what's running:**
   ```bash
   # See if Streamlit is running
   ps aux | grep streamlit
   
   # Kill if needed
   pkill -f streamlit
   ```

---

## 📚 **Documentation:**

- **This guide:** Local setup (you are here!)
- **PERSISTENT_SESSION_GUIDE.md:** Deep dive on authentication
- **AUTHENTICATION_QUICK_START.md:** Compare all auth methods
- **AUTODESK_IDSDK_GUIDE.md:** For cloud deployment

---

## ✅ **Success Checklist:**

Before you start using the automation, make sure:

- [ ] Node.js installed (`node --version`)
- [ ] Python installed (`python3 --version`)
- [ ] npm packages installed (`npm list`)
- [ ] Chromium browser installed (check `node_modules/playwright-core/.local-browsers/`)
- [ ] Virtual environment created (`ls venv/`)
- [ ] Streamlit installed (`source venv/bin/activate && python3 -c "import streamlit"`)
- [ ] Authentication configured (`ls auth/draftr-session.json`)
- [ ] Streamlit runs (`streamlit run app.py`)
- [ ] Browser opens to http://localhost:8501
- [ ] Automation shows: "🔐 Authentication: Persistent Browser Session"

**All checked?** You're ready! 🎉

---

## 🆘 **Need Help?**

If something doesn't work:

1. **Check error messages** - They usually tell you what's wrong
2. **Review troubleshooting section** (above)
3. **Re-run setup:**
   ```bash
   npm install
   npx playwright install chromium
   node setup_draftr_auth.js
   ```
4. **Start fresh:**
   ```bash
   rm -rf node_modules venv auth
   # Then run first-time setup again
   ```

---

## 🎉 **You're Ready!**

Your local Draftr automation is now set up!

**Start using it:**
```bash
cd streamlit_mdc_app
source venv/bin/activate
streamlit run app.py
```

**Open:** http://localhost:8501

**Enjoy! 🚀**

