# 🚀 Draftr API Integration Guide

**Using Draftr's API instead of browser automation** (if API exists)

---

## 🎯 **Why API is Better Than Cookies**

| Feature | 🍪 Cookies (Browser) | 🔌 API |
|---------|---------------------|--------|
| **Security** | ⚠️ Medium (session hijacking risk) | ✅ High (scoped tokens) |
| **Speed** | 🐌 Slow (5-10 seconds) | ⚡ Fast (<1 second) |
| **Reliability** | ⚠️ Can break with UI changes | ✅ Stable (versioned API) |
| **Maintenance** | ⚠️ Requires cookie rotation | ✅ Long-lived tokens |
| **Error Handling** | ⚠️ Vague (page not found) | ✅ Clear (HTTP status codes) |
| **Audit Trail** | ⚠️ Limited | ✅ Complete API logs |
| **Rate Limiting** | ❌ None (can overload) | ✅ Controlled |

---

## 📋 **Step 1: Discover if Draftr Has an API**

### **Method 1: Check Documentation**

Search for:
```
site:autodesk.com "Draftr API"
site:autodesk.com "Draftr developer"
site:autodesk.com "Draftr REST API"
```

Look for:
- API documentation portal
- Developer guides
- OpenAPI/Swagger specs
- API reference

### **Method 2: Inspect Network Traffic**

1. Open Draftr in browser
2. Open DevTools (F12) → **Network** tab
3. Filter by **XHR** or **Fetch**
4. Perform a link update manually
5. Look for API calls like:
   ```
   POST https://webpub.autodesk.com/api/v1/assets/3934720/links
   PUT https://api.draftr.com/v2/content/links/12345
   PATCH https://draftr.autodesk.com/api/assets/3934720
   ```

If you see these → **Draftr HAS an API!**

### **Method 3: Contact Autodesk**

Email/Slack your:
- Autodesk account manager
- Draftr administrator
- IT/DevOps team

**Template email:**
```
Subject: Draftr API Access for Link Update Automation

Hi [Name],

We're looking to automate link updates in Draftr email assets. 

Questions:
1. Does Draftr have a REST/GraphQL API?
2. Can we get API credentials (token/key)?
3. Is there API documentation available?
4. Can we create a service account for automation?

We need to programmatically update link URLs in assets like:
- Change specific link: "Get in touch" → new URL
- Bulk replace: old URL → new URL across all links
- Domain replace: /en/ → /uk/

Current approach uses browser automation which is slow and fragile.

Thanks!
```

---

## 🔑 **Step 2: Get API Credentials**

Once you confirm API exists, request:

### **Option A: API Key (Simplest)**
```
DRAFTR_API_KEY=draftr_live_abc123xyz789
```

### **Option B: OAuth 2.0**
```
DRAFTR_CLIENT_ID=your_client_id
DRAFTR_CLIENT_SECRET=your_client_secret
DRAFTR_TOKEN_URL=https://auth.autodesk.com/oauth/token
```

### **Option C: Service Account**
```
DRAFTR_SERVICE_ACCOUNT=automation@yourcompany.com
DRAFTR_SERVICE_TOKEN=service_token_here
```

---

## 🔧 **Step 3: Test API with curl**

Before coding, test with command line:

### **Example 1: Get Asset**
```bash
curl -X GET \
  'https://api.webpub.autodesk.com/draftr/v1/assets/3934720' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### **Example 2: Get Links**
```bash
curl -X GET \
  'https://api.webpub.autodesk.com/draftr/v1/assets/3934720/links' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### **Example 3: Update Link**
```bash
curl -X PATCH \
  'https://api.webpub.autodesk.com/draftr/v1/assets/3934720/links/12345' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://www.autodesk.com/uk/support"
  }'
```

**If these work → You're ready to integrate!**

---

## 💻 **Step 4: Add API Key to Streamlit Secrets**

### **Local Development:**

Edit `.streamlit/secrets.toml`:
```toml
# Draftr API Authentication
DRAFTR_API_KEY = "your_api_key_here"
DRAFTR_API_BASE_URL = "https://api.webpub.autodesk.com/draftr/v1"
```

### **Streamlit Cloud:**

1. Go to **Streamlit Cloud** → Your App → **Settings** → **Secrets**
2. Add:
```toml
# Draftr API Authentication
DRAFTR_API_KEY = "your_api_key_here"
DRAFTR_API_BASE_URL = "https://api.webpub.autodesk.com/draftr/v1"
```
3. Click **Save**

---

## 🚀 **Step 5: Use the API Client**

The `draftr_api_client.py` is already created! Here's how to use it:

### **Example 1: Update a Specific Link**

```python
from draftr_api_client import draftr_api_update_link

result = draftr_api_update_link(
    asset_id="3934720",
    link_text="Get in touch",
    new_url="www.autodesk.com/uk/support"
)

if result['success']:
    print(f"✅ Updated: {result['link_text']}")
    print(f"   Old: {result['old_url']}")
    print(f"   New: {result['new_url']}")
else:
    print(f"❌ Error: {result['error']}")
```

### **Example 2: Bulk Replace URLs**

```python
from draftr_api_client import draftr_api_bulk_replace

result = draftr_api_bulk_replace(
    asset_id="3934720",
    old_url="https://old-domain.com/page",
    new_url="https://new-domain.com/page"
)

print(f"✅ Updated {result['updated_count']} links")
```

### **Example 3: Replace Domain**

```python
from draftr_api_client import draftr_api_replace_domain

result = draftr_api_replace_domain(
    asset_id="3934720",
    old_domain="/en/",
    new_domain="/uk/"
)

print(f"✅ Updated {result['updated_count']} links")
```

---

## 📊 **Step 6: Compare Performance**

### **Browser Automation (Current):**
```
⏱️  Duration: 30-60 seconds per asset
🔄 Steps: Launch browser → Inject cookies → Navigate → Wait for JS → Find element → Click → Update → Save
❌ Failure points: 7+ (any can break)
```

### **API (Proposed):**
```
⏱️  Duration: <1 second per asset
🔄 Steps: API call → Update
❌ Failure points: 1 (API call)
```

**~50x faster and much more reliable!**

---

## 🔐 **Security Comparison**

### **Cookies:**
- ⚠️ Can access entire Draftr account
- ⚠️ All pages, all actions
- ⚠️ Like giving someone your session

### **API Token:**
- ✅ Scoped permissions (only what's needed)
- ✅ Can restrict to specific operations
- ✅ Easy to revoke and rotate
- ✅ Better audit trail

---

## 🎯 **Next Steps**

### **If API Exists:**

1. ✅ Get API credentials
2. ✅ Add to Streamlit secrets
3. ✅ Test with `draftr_api_client.py`
4. ✅ Remove browser automation code
5. ✅ Delete cookies from secrets

### **If NO API:**

1. Continue with cookie-based approach
2. Request API feature from Autodesk
3. Consider other automation tools (Selenium with better auth)

---

## 📝 **Reporting Your Findings**

After investigating, update this doc:

```markdown
## Investigation Results

**Date:** YYYY-MM-DD
**Investigated by:** Your Name

### Does Draftr Have an API?
- [ ] YES - API exists
- [ ] NO - No API available
- [ ] UNKNOWN - Need more info

### If YES:
- API Base URL: _______________
- Authentication method: _______________
- Documentation URL: _______________
- API version: _______________

### If NO:
- Alternative considered: _______________
- Recommendation: Continue with cookies / Request API feature
```

---

## 💡 **Pro Tip:**

Even if there's NO public API, there might be:
- Internal API (ask your Autodesk rep)
- Partner API (if you have enterprise agreement)
- Beta API (request early access)

Don't give up after one "no" - escalate if needed!

---

## 🚀 **Ready to Test?**

Run this to check if the API client works:

```python
# Test connection
from draftr_api_client import DraftrAPIClient

try:
    client = DraftrAPIClient()
    asset = client.get_asset("3934720")
    print("✅ API connection successful!")
    print(f"Asset title: {asset.get('title')}")
except Exception as e:
    print(f"❌ API connection failed: {e}")
    print("→ Draftr may not have an API, or credentials are wrong")
```

---

## ❓ **Questions?**

If you discover Draftr has an API, let me know:
1. The API base URL
2. Authentication method
3. Documentation link

I'll customize the implementation for your specific use case!

