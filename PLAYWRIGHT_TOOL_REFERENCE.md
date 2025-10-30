# Playwright MCP Server - Tool Reference

Based on official documentation: https://executeautomation.github.io/mcp-playwright/docs/playwright-web/Supported-Tools

## ✅ Correct Tool Naming Convention

Tools use **`Playwright_`** prefix (capital P) or **`playwright_`** prefix (lowercase p).

**NOT** `browser_`, `mcp_playwright-extension_`, or any other prefix.

---

## 📋 Most Common Tools

### Navigation & Page Control

#### `Playwright_navigate`
Navigate to a URL.

**Parameters:**
- `url` (string, required): URL to navigate to
- `browserType` (string, optional, default: "chromium"): Browser engine ("chromium", "firefox", "webkit")
- `width` (number, optional, default: 1280): Viewport width
- `height` (number, optional, default: 720): Viewport height
- `headless` (boolean, optional, default: false): Run in headless mode
- `timeout` (number, optional): Navigation timeout in ms
- `waitUntil` (string, optional): Wait condition

**Example:**
```json
{
  "tool": "Playwright_navigate",
  "params": {
    "url": "https://example.com",
    "headless": true,
    "width": 1920,
    "height": 1080
  }
}
```

---

#### `playwright_go_back`
Navigate back in browser history.

**Example:**
```json
{
  "tool": "playwright_go_back",
  "params": {}
}
```

---

#### `playwright_go_forward`
Navigate forward in browser history.

**Example:**
```json
{
  "tool": "playwright_go_forward",
  "params": {}
}
```

---

### Screenshots & Content

#### `Playwright_screenshot`
Capture screenshots of page or elements.

**Parameters:**
- `name` (string, required): Screenshot name
- `selector` (string, optional): CSS selector for specific element
- `width` (number, optional, default: 800): Screenshot width
- `height` (number, optional, default: 600): Screenshot height
- `fullPage` (boolean, optional, default: false): Capture full page
- `savePng` (boolean, optional, default: false): Save as PNG file
- `storeBase64` (boolean, optional, default: false): Store as base64
- `downloadsDir` (string, optional): Directory to save screenshot

**Example:**
```json
{
  "tool": "Playwright_screenshot",
  "params": {
    "name": "homepage",
    "fullPage": true,
    "savePng": true
  }
}
```

---

#### `playwright_get_visible_text`
Get the visible text content of the current page.

**Example:**
```json
{
  "tool": "playwright_get_visible_text",
  "params": {}
}
```

---

#### `playwright_get_visible_html`
Get the HTML content of the current page.

**Parameters:**
- `selector` (string, optional): CSS selector to limit HTML to specific container
- `removeScripts` (boolean, optional, default: false): Remove script tags
- `removeComments` (boolean, optional, default: false): Remove HTML comments
- `removeStyles` (boolean, optional, default: false): Remove style tags
- `removeMeta` (boolean, optional, default: false): Remove meta tags
- `minify` (boolean, optional, default: false): Minify HTML
- `cleanHtml` (boolean, optional, default: false): Combines all remove options

**Example:**
```json
{
  "tool": "playwright_get_visible_html",
  "params": {
    "cleanHtml": true,
    "selector": "main"
  }
}
```

---

### Interactions

#### `Playwright_click`
Click elements on the page.

**Parameters:**
- `selector` (string, required): CSS selector for element

**Example:**
```json
{
  "tool": "Playwright_click",
  "params": {
    "selector": "button#submit"
  }
}
```

---

#### `Playwright_fill`
Fill out input fields.

**Parameters:**
- `selector` (string, required): CSS selector for input field
- `value` (string, required): Value to fill

**Example:**
```json
{
  "tool": "Playwright_fill",
  "params": {
    "selector": "input[name='email']",
    "value": "test@example.com"
  }
}
```

---

#### `Playwright_select`
Select an option in a SELECT dropdown.

**Parameters:**
- `selector` (string, required): CSS selector for select element
- `value` (string, required): Value to select

**Example:**
```json
{
  "tool": "Playwright_select",
  "params": {
    "selector": "select#country",
    "value": "USA"
  }
}
```

---

#### `Playwright_hover`
Hover over elements.

**Parameters:**
- `selector` (string, required): CSS selector for element

**Example:**
```json
{
  "tool": "Playwright_hover",
  "params": {
    "selector": ".menu-item"
  }
}
```

---

#### `playwright_drag`
Drag an element to a target location.

**Parameters:**
- `sourceSelector` (string, required): CSS selector for element to drag
- `targetSelector` (string, required): CSS selector for target location

**Example:**
```json
{
  "tool": "playwright_drag",
  "params": {
    "sourceSelector": "#draggable",
    "targetSelector": "#dropzone"
  }
}
```

---

#### `playwright_press_key`
Press a keyboard key.

**Parameters:**
- `key` (string, required): Key to press (e.g., 'Enter', 'ArrowDown', 'a')
- `selector` (string, optional): CSS selector for element to focus first

**Example:**
```json
{
  "tool": "playwright_press_key",
  "params": {
    "key": "Enter",
    "selector": "input[type='search']"
  }
}
```

---

### File Operations

#### `playwright_upload_file`
Upload a file to an input[type='file'] element.

**Parameters:**
- `selector` (string, required): CSS selector for file input
- `filePath` (string, required): Absolute path to file

**Example:**
```json
{
  "tool": "playwright_upload_file",
  "params": {
    "selector": "input[type='file']",
    "filePath": "/Users/username/Documents/file.pdf"
  }
}
```

---

#### `playwright_save_as_pdf`
Save the current page as a PDF file.

**Parameters:**
- `outputPath` (string, required): Directory path for PDF
- `filename` (string, optional, default: "page.pdf"): PDF filename
- `format` (string, optional, default: "A4"): Page format
- `printBackground` (boolean, optional, default: true): Print background graphics
- `margin` (object, optional): Page margins (top, right, bottom, left)

**Example:**
```json
{
  "tool": "playwright_save_as_pdf",
  "params": {
    "outputPath": "/Users/username/Downloads",
    "filename": "report.pdf",
    "format": "A4",
    "printBackground": true
  }
}
```

---

### Advanced Features

#### `Playwright_evaluate`
Execute JavaScript in the browser console.

**Parameters:**
- `script` (string, required): JavaScript code to execute

**Example:**
```json
{
  "tool": "Playwright_evaluate",
  "params": {
    "script": "return document.title"
  }
}
```

---

#### `Playwright_console_logs`
Retrieve console logs from the browser.

**Parameters:**
- `search` (string, optional): Text to search for in logs
- `limit` (number, optional): Maximum number of logs
- `type` (string, optional): Type of logs (all, error, warning, log, info, debug, exception)
- `clear` (boolean, optional, default: false): Clear logs after retrieval

**Example:**
```json
{
  "tool": "Playwright_console_logs",
  "params": {
    "type": "error",
    "limit": 50
  }
}
```

---

#### `playwright_click_and_switch_tab`
Click a link and switch to newly opened tab.

**Parameters:**
- `selector` (string, required): CSS selector for link

**Example:**
```json
{
  "tool": "playwright_click_and_switch_tab",
  "params": {
    "selector": "a[target='_blank']"
  }
}
```

---

### Iframe Support

#### `Playwright_iframe_click`
Click elements inside an iframe.

**Parameters:**
- `iframeSelector` (string, required): CSS selector for iframe
- `selector` (string, required): CSS selector for element in iframe

**Example:**
```json
{
  "tool": "Playwright_iframe_click",
  "params": {
    "iframeSelector": "iframe#payment",
    "selector": "button.submit"
  }
}
```

---

#### `Playwright_iframe_fill`
Fill elements inside an iframe.

**Parameters:**
- `iframeSelector` (string, required): CSS selector for iframe
- `selector` (string, required): CSS selector for element in iframe
- `value` (string, required): Value to fill

**Example:**
```json
{
  "tool": "Playwright_iframe_fill",
  "params": {
    "iframeSelector": "iframe#payment",
    "selector": "input[name='cardNumber']",
    "value": "4242424242424242"
  }
}
```

---

### HTTP Response Monitoring

#### `Playwright_expect_response`
Start waiting for an HTTP response.

**Parameters:**
- `id` (string, required): Unique identifier for later retrieval
- `url` (string, required): URL pattern to match

**Example:**
```json
{
  "tool": "Playwright_expect_response",
  "params": {
    "id": "api-call-1",
    "url": "https://api.example.com/data"
  }
}
```

---

#### `Playwright_assert_response`
Wait for and validate a previously initiated HTTP response.

**Parameters:**
- `id` (string, required): Identifier from `Playwright_expect_response`
- `value` (string, optional): Expected data in response body

**Example:**
```json
{
  "tool": "Playwright_assert_response",
  "params": {
    "id": "api-call-1",
    "value": "success"
  }
}
```

---

### Utilities

#### `playwright_custom_user_agent`
Set a custom User Agent.

**Parameters:**
- `userAgent` (string, required): Custom User Agent string

**Example:**
```json
{
  "tool": "playwright_custom_user_agent",
  "params": {
    "userAgent": "Mozilla/5.0 (Custom Bot) Chrome/120.0"
  }
}
```

---

#### `Playwright_close`
Close the browser and release resources.

**Example:**
```json
{
  "tool": "Playwright_close",
  "params": {}
}
```

---

## 📝 Code Generation Tools

### `start_codegen_session`
Start recording Playwright actions.

**Parameters:**
- `options` (object, required):
  - `outputPath` (string, required): Directory for generated tests
  - `testNamePrefix` (string, optional, default: "GeneratedTest"): Test name prefix
  - `includeComments` (boolean, optional): Include comments in generated code

---

### `end_codegen_session`
End recording and generate test file.

**Parameters:**
- `sessionId` (string, required): Session ID from start_codegen_session

---

### `get_codegen_session`
Get information about a code generation session.

**Parameters:**
- `sessionId` (string, required): Session ID

---

### `clear_codegen_session`
Clear a session without generating test.

**Parameters:**
- `sessionId` (string, required): Session ID

---

## 🎯 Quick Reference

| Task | Tool |
|------|------|
| Navigate to URL | `Playwright_navigate` |
| Click element | `Playwright_click` |
| Fill input | `Playwright_fill` |
| Select dropdown | `Playwright_select` |
| Take screenshot | `Playwright_screenshot` |
| Get page text | `playwright_get_visible_text` |
| Get page HTML | `playwright_get_visible_html` |
| Execute JavaScript | `Playwright_evaluate` |
| Get console logs | `Playwright_console_logs` |
| Upload file | `playwright_upload_file` |
| Press keyboard key | `playwright_press_key` |
| Drag and drop | `playwright_drag` |
| Hover over element | `Playwright_hover` |
| Go back | `playwright_go_back` |
| Go forward | `playwright_go_forward` |
| Close browser | `Playwright_close` |

---

## 🔗 Official Documentation

Full documentation: https://executeautomation.github.io/mcp-playwright/docs/playwright-web/Supported-Tools

