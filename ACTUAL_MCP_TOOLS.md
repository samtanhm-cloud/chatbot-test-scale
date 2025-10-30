# ACTUAL Playwright MCP Tools

**⚠️ IMPORTANT: The official documentation is OUTDATED!**

The docs show `Playwright_navigate` (capital P), but the actual tool names use **lowercase** `playwright_` prefix.

This guide shows the **REAL, WORKING** tool names verified from the running MCP server.

---

## 🔍 How to Verify Tool Names

Run this command to see all available tools:
```bash
node list_mcp_tools.js
```

---

## 📋 All Available Tools (32 Total)

### Code Generation (4 tools)

1. **`start_codegen_session`** - Start recording Playwright actions
2. **`end_codegen_session`** - End recording and generate test file
3. **`get_codegen_session`** - Get session information
4. **`clear_codegen_session`** - Clear session without generating test

---

### Navigation & Page Control (3 tools)

#### `playwright_navigate`
Navigate to a URL.

**Example:**
```json
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://example.com"
  }
}
```

#### `playwright_go_back`
Navigate back in browser history.

```json
{
  "tool": "playwright_go_back",
  "params": {}
}
```

#### `playwright_go_forward`
Navigate forward in browser history.

```json
{
  "tool": "playwright_go_forward",
  "params": {}
}
```

---

### Screenshots & Content (4 tools)

#### `playwright_screenshot`
Take a screenshot of the page or element.

**Example:**
```json
{
  "tool": "playwright_screenshot",
  "params": {
    "name": "homepage",
    "width": 1280,
    "height": 720
  }
}
```

#### `playwright_get_visible_text`
Get the visible text content of the current page.

```json
{
  "tool": "playwright_get_visible_text",
  "params": {}
}
```

#### `playwright_get_visible_html`
Get the HTML content of the current page.

```json
{
  "tool": "playwright_get_visible_html",
  "params": {}
}
```

#### `playwright_save_as_pdf`
Save page as PDF.

```json
{
  "tool": "playwright_save_as_pdf",
  "params": {
    "outputPath": "/path/to/save",
    "filename": "page.pdf"
  }
}
```

---

### Interactions (9 tools)

#### `playwright_click`
Click an element on the page.

**Example:**
```json
{
  "tool": "playwright_click",
  "params": {
    "selector": "button#submit"
  }
}
```

#### `playwright_fill`
Fill out an input field.

```json
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[name='email']",
    "value": "test@example.com"
  }
}
```

#### `playwright_select`
Select an option in a SELECT dropdown.

```json
{
  "tool": "playwright_select",
  "params": {
    "selector": "select#country",
    "value": "USA"
  }
}
```

#### `playwright_hover`
Hover over an element.

```json
{
  "tool": "playwright_hover",
  "params": {
    "selector": ".menu-item"
  }
}
```

#### `playwright_drag`
Drag and drop.

```json
{
  "tool": "playwright_drag",
  "params": {
    "sourceSelector": "#draggable",
    "targetSelector": "#dropzone"
  }
}
```

#### `playwright_press_key`
Press a keyboard key.

```json
{
  "tool": "playwright_press_key",
  "params": {
    "key": "Enter",
    "selector": "input[type='search']"
  }
}
```

#### `playwright_upload_file`
Upload a file.

```json
{
  "tool": "playwright_upload_file",
  "params": {
    "selector": "input[type='file']",
    "filePath": "/absolute/path/to/file.pdf"
  }
}
```

#### `playwright_click_and_switch_tab`
Click a link and switch to new tab.

```json
{
  "tool": "playwright_click_and_switch_tab",
  "params": {
    "selector": "a[target='_blank']"
  }
}
```

#### `playwright_double_click`
Double-click an element.

```json
{
  "tool": "playwright_double_click",
  "params": {
    "selector": ".editable-field"
  }
}
```

---

### Iframe Support (2 tools)

#### `playwright_iframe_click`
Click element inside an iframe.

```json
{
  "tool": "playwright_iframe_click",
  "params": {
    "iframeSelector": "iframe#payment",
    "selector": "button.submit"
  }
}
```

#### `playwright_iframe_fill`
Fill element inside an iframe.

```json
{
  "tool": "playwright_iframe_fill",
  "params": {
    "iframeSelector": "iframe#payment",
    "selector": "input[name='cardNumber']",
    "value": "4242424242424242"
  }
}
```

---

### HTTP API Tools (5 tools)

#### `playwright_get`
Perform HTTP GET request.

```json
{
  "tool": "playwright_get",
  "params": {
    "url": "https://api.example.com/data"
  }
}
```

#### `playwright_post`
Perform HTTP POST request.

```json
{
  "tool": "playwright_post",
  "params": {
    "url": "https://api.example.com/data",
    "data": {"key": "value"}
  }
}
```

#### `playwright_put`
Perform HTTP PUT request.

```json
{
  "tool": "playwright_put",
  "params": {
    "url": "https://api.example.com/data/1",
    "data": {"key": "new_value"}
  }
}
```

#### `playwright_patch`
Perform HTTP PATCH request.

```json
{
  "tool": "playwright_patch",
  "params": {
    "url": "https://api.example.com/data/1",
    "data": {"key": "updated_value"}
  }
}
```

#### `playwright_delete`
Perform HTTP DELETE request.

```json
{
  "tool": "playwright_delete",
  "params": {
    "url": "https://api.example.com/data/1"
  }
}
```

---

### HTTP Response Monitoring (2 tools)

#### `playwright_expect_response`
Start waiting for an HTTP response.

```json
{
  "tool": "playwright_expect_response",
  "params": {
    "id": "api-call-1",
    "url": "https://api.example.com/data"
  }
}
```

#### `playwright_assert_response`
Validate a previously expected response.

```json
{
  "tool": "playwright_assert_response",
  "params": {
    "id": "api-call-1",
    "value": "expected_data"
  }
}
```

---

### Utilities (3 tools)

#### `playwright_evaluate`
Execute JavaScript in browser console.

```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "return document.title"
  }
}
```

#### `playwright_console_logs`
Retrieve console logs from browser.

```json
{
  "tool": "playwright_console_logs",
  "params": {
    "type": "error",
    "limit": 50
  }
}
```

#### `playwright_custom_user_agent`
Set custom User Agent.

```json
{
  "tool": "playwright_custom_user_agent",
  "params": {
    "userAgent": "Mozilla/5.0 (Custom Bot)"
  }
}
```

#### `playwright_close`
Close browser and release resources.

```json
{
  "tool": "playwright_close",
  "params": {}
}
```

---

## 🎯 Quick Reference Table

| What You Want | Tool Name |
|---------------|-----------|
| Navigate to URL | `playwright_navigate` |
| Click element | `playwright_click` |
| Fill input | `playwright_fill` |
| Select dropdown | `playwright_select` |
| Take screenshot | `playwright_screenshot` |
| Get page text | `playwright_get_visible_text` |
| Get page HTML | `playwright_get_visible_html` |
| Execute JavaScript | `playwright_evaluate` |
| Get console logs | `playwright_console_logs` |
| Upload file | `playwright_upload_file` |
| Press key | `playwright_press_key` |
| Drag and drop | `playwright_drag` |
| Hover | `playwright_hover` |
| Go back | `playwright_go_back` |
| Go forward | `playwright_go_forward` |
| Close browser | `playwright_close` |
| HTTP GET | `playwright_get` |
| HTTP POST | `playwright_post` |

---

## ⚠️ Key Differences from Documentation

| Documentation Says | Actually Is |
|--------------------|-------------|
| `Playwright_navigate` | `playwright_navigate` |
| `Playwright_screenshot` | `playwright_screenshot` |
| `Playwright_click` | `playwright_click` |
| `Playwright_fill` | `playwright_fill` |

**ALL tools use lowercase `playwright_` prefix, NOT capital `Playwright_`!**

---

## 🔗 Links

- Official (outdated) docs: https://executeautomation.github.io/mcp-playwright/docs/playwright-web/Supported-Tools
- To verify current tools: Run `node list_mcp_tools.js`

