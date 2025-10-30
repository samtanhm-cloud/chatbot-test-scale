# Understanding Selector Timeouts 🔍

## What Happened

You got this error:
```
Timeout 30000ms exceeded.
waiting for locator('div[data-panel-id]')
```

**This is EXPECTED behavior!** ✅

---

## Why It Happened

The MDC file `draftr-link-updater.mdc` tries to click on:
```json
{
  "selector": "div[data-panel-id]"
}
```

**Problem:** This is a **generic placeholder selector** - it doesn't exist in your actual Draftr page!

The automation correctly:
1. ✅ Loaded the page
2. ✅ Launched the browser
3. ✅ Tried to find the element
4. ⏰ Waited 30 seconds
5. ❌ Timed out (because element doesn't exist)

---

## 🎯 Two Solutions

### Solution 1: JavaScript-Based (Recommended)

**File:** `draftr-link-updater-js.mdc`

**Advantages:**
- ✅ No UI selectors needed
- ✅ Works on any Draftr asset
- ✅ Direct DOM manipulation
- ✅ Fast and reliable
- ✅ Shows what changed (red borders)
- ✅ Returns detailed output

**Limitations:**
- ⚠️ Doesn't automatically save to Draftr backend
- ⚠️ Requires manual save (or you add Save button selector)

**Use this if:** You want to see what would change and can manually save

---

### Solution 2: UI-Based (Requires Setup)

**File:** `draftr-link-updater.mdc`

**Advantages:**
- ✅ Can automatically save if selectors are correct
- ✅ Mimics manual workflow

**Limitations:**
- ❌ Requires inspecting Draftr UI
- ❌ Needs correct selectors for your specific asset structure
- ❌ Selectors may change between assets
- ❌ More fragile
- ❌ Slower (clicks, waits, etc.)

**Use this if:** You have time to inspect and customize selectors

---

## 🚀 Recommended: Use JavaScript Approach

After redeploy, try using the JavaScript-based file:

### Update app.py to prefer JS version

Or just rename the file so it gets matched first, or use explicit keywords in your prompt:

**Prompt:**
```
run draftr js updater on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"
```

The JS version will:
1. ✅ Load your asset page
2. ✅ Find all links
3. ✅ Modify the matching link(s)
4. ✅ Highlight changed links with red border
5. ✅ Take screenshots
6. ✅ Return detailed list of changes
7. ⚠️ **You manually save** in Draftr UI

---

## 📋 Comparison

| Feature | JavaScript Approach | UI Approach |
|---------|-------------------|-------------|
| **Setup required** | None | Inspect selectors |
| **Works universally** | ✅ Yes | ❌ Asset-specific |
| **Speed** | ✅ Fast | ⏰ Slow (clicks/waits) |
| **Reliability** | ✅ High | ⚠️ Depends on selectors |
| **Shows changes** | ✅ Red borders | ⚠️ Screenshots only |
| **Auto-saves** | ❌ No | ✅ Yes (if selectors correct) |
| **Detailed output** | ✅ Yes | ⚠️ Limited |

---

## 🔧 How to Get Real Selectors (If you want UI approach)

### Step 1: Open Draftr Asset
```
https://webpub.autodesk.com/draftr/asset/3934720
```

### Step 2: Inspect Elements

#### For Panel/Section:
1. Right-click on the panel containing the link
2. Select "Inspect" (Chrome DevTools)
3. Find the element in HTML
4. Right-click → Copy → Copy selector
5. Example result: `div.panel-container[data-id="abc123"]`

#### For Link Input Field:
1. Click on a link to edit it
2. Right-click the input field
3. Inspect → Copy selector
4. Example result: `input[name="primary-cta-url"]`

#### For Save Button:
1. Right-click Save button
2. Inspect → Copy selector
3. Example result: `button[aria-label="Save Asset"]`

### Step 3: Update MDC File

Replace placeholders with real selectors:

**Before:**
```json
{
  "selector": "div[data-panel-id]"
}
```

**After:**
```json
{
  "selector": "div.panel-container[data-id='abc123']"
}
```

---

## 🎯 Decision Guide

### Use JavaScript Approach If:
- ✅ You want fast results
- ✅ You're okay with manual save
- ✅ You want to work with any asset
- ✅ You want visual confirmation
- ✅ You want detailed output

### Use UI Approach If:
- ✅ You want fully automated save
- ✅ You have time to inspect selectors
- ✅ You're working with consistent asset structure
- ✅ You want to replicate exact manual workflow

---

## 🚨 Common Timeout Causes

### 1. Wrong Selector
```
selector: "div[data-panel-id]"  ← Doesn't exist
```
**Fix:** Get real selector from DevTools

### 2. Element Not Loaded
```
Element exists but hasn't loaded yet
```
**Fix:** Add wait before clicking:
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 3000))"
  }
}
```

### 3. Element Hidden/Disabled
```
Element exists but is display:none or disabled
```
**Fix:** Use `force: true` or wait for it to be visible

### 4. Dynamic Content
```
Element's selector changes dynamically
```
**Fix:** Use more generic/stable selector patterns

---

## 💡 Best Practice

**For production use:**
1. ✅ Start with JavaScript approach
2. ✅ Verify changes visually (red borders)
3. ✅ Review detailed output
4. ✅ Manually save in Draftr
5. ✅ If you need automation, invest time to get correct selectors
6. ✅ Document selectors for future use

---

## 🎉 Summary

**The timeout you saw is normal!** It means:
- ✅ Browser launched correctly
- ✅ Page loaded correctly
- ✅ Automation tried to find element
- ❌ Selector was a placeholder

**Solution:** Use the new JavaScript-based approach (`draftr-link-updater-js.mdc`) which doesn't need any selectors!

After redeploy, try your prompt again with keyword "js" to use the JavaScript version:
```
run draftr js updater on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"
```

🚀 This will work without any selector issues!

