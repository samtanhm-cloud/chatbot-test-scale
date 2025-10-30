# JavaScript Syntax Fix - playwright_evaluate

## 🐛 The Bug

When using `playwright_evaluate` for wait/delay commands, I initially wrote:

❌ **WRONG:**
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "return new Promise(resolve => setTimeout(resolve, 5000))"
  }
}
```

**Error:**
```
SyntaxError: Illegal return statement
```

**Why it fails:** The `return` keyword can ONLY be used inside a function. This code tried to use `return` at the top level, which is invalid JavaScript.

---

## ✅ The Fix

Wrap the code in an arrow function:

✅ **CORRECT:**
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 5000))"
  }
}
```

**Why it works:** The `() =>` creates an arrow function. Now the Promise is the return value of that function, which is valid JavaScript.

---

## 📋 playwright_evaluate Rules

The `script` parameter must contain **valid JavaScript** that can be evaluated by `page.evaluate()`.

### Valid Formats:

#### 1. Arrow Function (Recommended)
```json
{
  "script": "() => document.title"
}
```

#### 2. Arrow Function with Block
```json
{
  "script": "() => { return document.title; }"
}
```

#### 3. Arrow Function Returning Promise (for async operations)
```json
{
  "script": "() => new Promise(resolve => setTimeout(resolve, 2000))"
}
```

#### 4. Complex Arrow Function
```json
{
  "script": "() => { const links = []; document.querySelectorAll('a').forEach(a => links.push(a.href)); return links; }"
}
```

### Invalid Formats:

❌ **Standalone return statement:**
```json
{
  "script": "return document.title"
}
```

❌ **Promise without function wrapper:**
```json
{
  "script": "new Promise(resolve => setTimeout(resolve, 2000))"
}
```

---

## 🔧 Common Use Cases

### Wait/Delay (2 seconds)
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => new Promise(resolve => setTimeout(resolve, 2000))"
  }
}
```

### Get Page Title
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => document.title"
  }
}
```

### Get Current URL
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => window.location.href"
  }
}
```

### Extract Links
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => { const links = []; document.querySelectorAll('a[href]').forEach((a, i) => { links.push({ index: i, href: a.href, text: a.textContent.trim() }); }); return links; }"
  }
}
```

### Check if Element Exists
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => document.querySelector('button#submit') !== null"
  }
}
```

### Get Element Text
```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => document.querySelector('h1')?.textContent || 'Not found'"
  }
}
```

---

## 🎯 What Was Fixed

### Files Updated:
- `draftr-link-updater-automation.mdc` - All 6 wait commands fixed
- `test-wait-simple.mdc` - New test file to verify correct syntax

### Changes Made:
All wait commands changed from:
```javascript
"return new Promise(...)"
```
To:
```javascript
"() => new Promise(...)"
```

---

## 🧪 Testing

### Simple Test
Try the new test file:
```
test wait simple
```

This will:
1. Navigate to example.com
2. Wait 2 seconds (tests the fix)
3. Get page title
4. Get visible text
5. Take screenshot

### Full Automation
Once the simple test works, try:
```
draftr link updater
```

---

## 💡 Key Takeaway

**Always wrap your JavaScript code in an arrow function when using `playwright_evaluate`:**

```json
{
  "script": "() => yourCodeHere"
}
```

This ensures the code is executed in a proper function context and can use `return` statements, `await`, and other function-level features.

---

## 📖 Related

- **Official Playwright docs:** https://playwright.dev/docs/api/class-page#page-evaluate
- **Arrow functions:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions
- **Promises:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise

---

## ✅ Status

All files are now fixed and pushed to GitHub. Streamlit should auto-redeploy with the corrected syntax.

