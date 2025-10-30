# 🚀 Deployment Guide

## Quick Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
# Navigate to app directory
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

# Check status (secrets.toml should NOT appear)
git status

# Add and commit
git add .
git commit -m "Update MDC Automation Executor"

# Push
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Click **"New app"**
3. Repository: `samtanhm-cloud/chatbot-test-scale`
4. Branch: `main`
5. Main file: `app.py`

### Step 3: Configure Secrets

**BEFORE deploying**, click **"Advanced settings" → "Secrets"**

Paste this configuration:

```toml
# Azure OpenAI with Azure AD Authentication
OPENAI_API_TYPE = "azure_ad"
AZURE_TENANT_ID = "67bff79e-7f91-4433-a8e5-c9252d2ddc1d"
AZURE_CLIENT_ID = "39ea943f-10b0-4caf-8145-02be6ee62564"
AZURE_CLIENT_SECRET = "61461b3c-f7a2-45e0-88f9-d09865bec9f8"
OPENAI_API_BASE = "https://cog-sandbox-dev-eastus2-001.openai.azure.com/"
OPENAI_API_VERSION = "2024-02-15-preview"
OPENAI_DEPLOYMENT_NAME = "gpt-5"
MCP_SERVER_URL = "http://localhost:3000"
```

### Step 4: Deploy!

Click **"Deploy"** and wait 2-5 minutes.

---

## Verify Deployment

Once deployed, check:
- ✅ Sidebar shows "🟢 AI Connected"
- ✅ MDC files are detected
- ✅ Can execute test automation

---

## Update Deployed App

To update your app after changes:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will automatically redeploy!

---

## Update Secrets

To change secrets after deployment:
1. Go to app dashboard
2. Click **⋮ menu → Settings**
3. Click **"Secrets"** tab
4. Edit and save

---

## Troubleshooting

**"Azure AD authentication failed"**
- Verify secrets in dashboard
- Check tenant ID, client ID, and secret

**"Deployment 'gpt-5' not found"**
- Change `OPENAI_DEPLOYMENT_NAME` to your actual deployment
- Common values: `gpt-4`, `gpt-35-turbo`

**"Module not found"**
- Check `requirements.txt` has all dependencies
- Commit and push changes

---

**Your app will be live at:** `https://your-app-name.streamlit.app`


