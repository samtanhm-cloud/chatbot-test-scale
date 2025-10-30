# Parameter Fixes for Draftr Automation

## ✅ All MDC Files Updated!

Your `draftr-link-updater-automation.mdc` file has been updated with the correct parameter names for all Playwright MCP tools.

---

## 🔧 What Was Fixed

### 1. **Screenshot Parameters**
❌ **Was Using:**
```json
{
  "tool": "playwright_screenshot",
  "params": {
    "filename": "draftr-auth-check.png",
    "type": "png"
  }
}
```

✅ **Fixed To:**
```json
{
  "tool": "playwright_screenshot",
  "params": {
    "name": "draftr-auth-check"
  }
}
```

**Why:** The tool uses `name` (not `filename`), and automatically handles PNG format.

---

### 2. **Wait/Sleep Commands**
❌ **Was Using:**
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "time": 5
  }
}
```

✅ **Fixed To:**
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "return new Promise(resolve => setTimeout(resolve, 5000))"
  }
}
```

**Why:** `playwright_evaluate` needs a JavaScript `script` parameter. To wait, we use `setTimeout` wrapped in a Promise.

---

### 3. **JavaScript Execution**
❌ **Was Using:**
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "function": "() => { return document.title; }"
  }
}
```

✅ **Fixed To:**
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => { return document.title; }"
  }
}
```

**Why:** Parameter is called `script` (not `function`).

---

### 4. **Click Actions**
❌ **Was Using:**
```json
{
  "tool": "playwright_click",
  "params": {
    "element": "Main Save button",
    "ref": "button[aria-label*='Save']"
  }
}
```

✅ **Fixed To:**
```json
{
  "tool": "playwright_click",
  "params": {
    "selector": "button[aria-label*='Save']"
  }
}
```

**Why:** The tool only uses `selector` (not `element` and `ref`). The `element` and `ref` parameters were from a different MCP server.

---

### 5. **Fill Actions**
❌ **Was Using:**
```json
{
  "tool": "playwright_fill",
  "params": {
    "element": "Link input field",
    "ref": "input[name*='link']",
    "text": "https://example.com"
  }
}
```

✅ **Fixed To:**
```json
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[name*='link']",
    "value": "https://example.com"
  }
}
```

**Why:** The tool uses `selector` (not `element`/`ref`) and `value` (not `text`).

---

## 📋 Correct Parameter Reference

### Most Common Tools

| Tool | Parameters | Example |
|------|-----------|---------|
| `playwright_navigate` | `url` | `{"url": "https://example.com"}` |
| `playwright_click` | `selector` | `{"selector": "button#submit"}` |
| `playwright_fill` | `selector`, `value` | `{"selector": "input", "value": "text"}` |
| `playwright_screenshot` | `name` | `{"name": "my-screenshot"}` |
| `playwright_evaluate` | `script` | `{"script": "return document.title"}` |
| `playwright_press_key` | `key` | `{"key": "Enter"}` |
| `playwright_select` | `selector`, `value` | `{"selector": "select", "value": "option1"}` |
| `playwright_get_visible_text` | (none) | `{}` |
| `playwright_get_visible_html` | (optional) | `{"selector": "main"}` |

---

## 🎯 Your Automation Is Now Ready!

All 3 MDC files are fixed:
1. ✅ `test-browser-simple.mdc` - Simple test (working!)
2. ✅ `test-mcp-tools.mdc` - Tool verification (working!)
3. ✅ `draftr-link-updater-automation.mdc` - **Your main automation** (fixed!)

---

## 🚀 Next Steps

### Test Your Draftr Automation

After Streamlit redeploys:

1. **Type in your app:** `draftr link updater`
2. **It should:**
   - ✅ Navigate to Draftr
   - ✅ Load the asset
   - ✅ Extract links
   - ✅ Enter edit mode
   - ✅ Update link URLs
   - ✅ Save changes
   - ✅ Verify updates

### Customize for Your Needs

**Key things to update in the MDC file:**

1. **Line 82 & 298:** Asset ID
   ```json
   "url": "https://webpub.autodesk.com/draftr/asset/YOUR_ASSET_ID"
   ```

2. **Line 199:** New URL to update to
   ```json
   "value": "https://your-new-url.com"
   ```

3. **Lines 144, 177, 256:** Selectors (may need to inspect Draftr UI)
   ```json
   "selector": "div[data-panel-id]"  // Update based on actual DOM
   ```

---

## 📖 Full Tool Reference

See these files for complete tool documentation:
- `ACTUAL_MCP_TOOLS.md` - All 32 tools with examples
- `list_mcp_tools.js` - Script to verify available tools

---

## 💡 Pro Tips

### Wait Times
Use `playwright_evaluate` with Promise timeout for waits:
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "return new Promise(resolve => setTimeout(resolve, 3000))"
  }
}
```

### Debugging
- Take screenshots frequently (`playwright_screenshot`)
- Get page text to verify state (`playwright_get_visible_text`)
- Check console logs (`playwright_console_logs`)

### Selectors
- Use browser DevTools to inspect elements
- Test selectors in browser console: `document.querySelector("your-selector")`
- Prefer specific selectors: IDs > data attributes > classes

---

## ✅ What's Working Now

1. ✅ **Correct tool names** (lowercase `playwright_`)
2. ✅ **Correct parameters** (`name` not `filename`, `selector` not `ref`, etc.)
3. ✅ **Browser installed** and working in headless mode
4. ✅ **All waits** properly implemented with JavaScript Promises
5. ✅ **All screenshots** using correct syntax
6. ✅ **All clicks/fills** using correct parameter names

---

## 🎉 You're All Set!

Your automation should now work end-to-end. Test it and let me know if you need any adjustments!

