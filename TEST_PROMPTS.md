# Test Prompts for Draftr Automation

**Updated for 3-minute manual login window**

---

## ✅ OPTION 1: Simple Test (RECOMMENDED TO START)

### Prompt:
```
Test save button for Draftr asset 3934720
```

### What it does:
- ✅ Opens Chrome (visible)
- ✅ Navigates to Draftr asset
- ⏰ **Waits 3 minutes for you to log in**
- ✅ Analyzes Save button
- ✅ Takes screenshots
- ✅ Returns button selectors

### MDC File Used:
`draftr-save-test.mdc`

### Variables Required:
- `asset_id`: 3934720

---

## ✅ OPTION 2: Full Link Update

### Prompt:
```
Update link in Draftr asset 3934720 to www.autodesk.com/uk/support with link text "Get in touch"
```

### What it does:
- ✅ Opens Chrome (visible)
- ✅ Navigates to Draftr asset
- ⏰ **Waits 3 minutes for you to log in**
- ✅ Extracts all links
- ✅ Updates specified link
- ✅ Clicks Save
- ✅ Takes before/after screenshots

### MDC File Used:
`draftr-link-updater.mdc`

### Variables Required:
- `asset_id`: 3934720
- `new_url`: www.autodesk.com/uk/support
- `link_text`: "Get in touch" (REQUIRED - must specify which link to update)

---

## 🚫 AVOID THESE PROMPTS

### ❌ Don't use:
```
Check asset 3934720 in Draftr
```
**Problem:** Might select the wrong MDC file

### ❌ Don't use:
```
Update link to www.autodesk.com/uk/support
```
**Problem:** Missing `asset_id` and `link_text` variables

---

## 📋 What Happens During Execution

### Timeline:

**0:00** - You submit prompt in Streamlit
```
[MDC Executor] Starting execution...
```

**0:01** - Chrome opens (VISIBLE window)
```
[MCP Server] Browser launched: Chrome
```

**0:02** - Navigates to Draftr
```
[MCP Server] Navigating to: https://webpub.autodesk.com/draftr/asset/3934720
```

**0:03** - ⏸️ **BROWSER PAUSES WITH ALERT DIALOG**
```
📢 You'll see a popup that says:
  "⏸️ AUTOMATION PAUSED
   🔐 Please log in to Draftr now
   ✅ Click OK when logged in and ready to continue"

⏰ Take as long as you need to:
  1. Click "Sign In" in Draftr
  2. Enter Autodesk credentials
  3. Complete 2FA if needed
  4. Wait for page to fully load
  5. Click OK in the alert dialog
```

**After clicking OK** - Automation continues immediately
```
[MCP Server] Taking screenshot...
[MCP Server] Running analysis...
```

**3:05** - Results returned
```
✅ Success!
```

---

## 🎯 RECOMMENDED FIRST TEST

**Copy and paste this exact prompt:**

```
Test save button for Draftr asset 3934720
```

**Then:**
1. Click "▶️ Execute" in Streamlit
2. Watch for Chrome window to open
3. Log in to Draftr manually
4. Wait 3 minutes for automation to continue
5. Check results

---

## 🔧 If Something Goes Wrong

### Error: "No commands found in MDC file"
**Solution:** You're using the wrong prompt. Use one of the exact prompts above.

### Error: "Unsubstituted variables: {{link_text}}"
**Solution:** Add the link text to your prompt:
```
... with link text "Get in touch"
```

### Error: "Browser not found"
**Solution:** Run:
```bash
cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"
npx playwright install chrome
```

### Chrome closes too quickly / Can't see the alert
**Solution:** The browser is now VISIBLE and uses a blocking JavaScript alert that pauses until you click OK

---

## ✅ START HERE

```
Test save button for Draftr asset 3934720
```

**Click Execute and watch Chrome open!** 🚀

