# Variable Substitution in MDC Files 🎯

**NEW FEATURE!** MDC files now support variables, making automation reusable and dynamic.

---

## 🌟 What This Means

Instead of hardcoding values in MDC files, you can use **{{variable}}** placeholders that get replaced with values from your prompt!

### Before (Hardcoded):
```json
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://webpub.autodesk.com/draftr/asset/3934202"
  }
}
```
❌ **Problem:** Have to edit MDC file for each different asset ID

### After (With Variables):
```json
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://webpub.autodesk.com/draftr/asset/{{asset_id}}"
  }
}
```
✅ **Solution:** Just change your prompt! No MDC file editing needed.

---

## 📝 How to Use Variables

### Step 1: Write MDC File with Variables

Use `{{variable_name}}` syntax anywhere in your MDC file:

```mcp
### Navigate to Draftr asset
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://webpub.autodesk.com/draftr/asset/{{asset_id}}"
  }
}
```

### Step 2: Use Natural Prompts

The system automatically extracts variables from your prompts:

**Example Prompts:**
- "run draftr updater on asset 3934720 and change link to www.autodesk.com/uk/support"
- "update draftr asset 123456 link to example.com"
- "change link in draftr 789012 to newurl.com"

**Extracted Variables:**
- `asset_id`: 3934720, 123456, 789012
- `new_url`: www.autodesk.com/uk/support, example.com, newurl.com

---

## 🎨 Variable Syntax

### Basic Syntax
```
{{variable_name}}
```

### Common Variables

| Variable | Description | Example Values |
|----------|-------------|----------------|
| `{{asset_id}}` | Draftr asset ID | 3934720, 123456 |
| `{{new_url}}` | URL to update | www.autodesk.com/uk/support |
| `{{link_text}}` | Text of link | "Get in touch", "Contact us" |
| `{{custom_var}}` | Any custom variable | Your value |

---

## 📋 Complete Example

### MDC File: `draftr-link-updater.mdc`

```mcp
# Draftr Link Updater

Updates links in Draftr asset {{asset_id}} to {{new_url}}

## Step 1: Navigate to asset
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://webpub.autodesk.com/draftr/asset/{{asset_id}}"
  }
}
```

```mcp
## Step 2: Fill new URL
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[name*='link']",
    "value": "{{new_url}}"
  }
}
```

```mcp
## Step 3: Take screenshot
{
  "tool": "playwright_screenshot",
  "params": {
    "name": "asset-{{asset_id}}-updated"
  }
}
```

### User Prompt:
```
run draftr updater on asset 3934720 and change link to www.autodesk.com/uk/support
```

### Execution Result:

**Variables Extracted:**
- `asset_id` → `3934720`
- `new_url` → `www.autodesk.com/uk/support`

**Actual Commands Executed:**
1. Navigate to: `https://webpub.autodesk.com/draftr/asset/3934720`
2. Fill input with: `www.autodesk.com/uk/support`
3. Screenshot saved as: `asset-3934720-updated.png`

---

## 🧠 How Variable Extraction Works

### Method 1: AI Extraction (Primary)
The system uses OpenAI to intelligently extract variables from your prompt:

```
Prompt: "run draftr updater on asset 3934720 and change link to www.autodesk.com/uk/support"

AI extracts:
{
  "asset_id": "3934720",
  "new_url": "www.autodesk.com/uk/support"
}
```

### Method 2: Regex Fallback (Backup)
If AI fails, regex patterns extract variables:

**Asset ID Patterns:**
- `asset 3934720` → extracts `3934720`
- `asset=123456` → extracts `123456`
- `on 3934720` → extracts `3934720`

**URL Patterns:**
- `to www.example.com` → extracts `www.example.com`
- `link to example.com/path` → extracts `example.com/path`
- `url: https://example.com` → extracts `example.com`
- `change ... to newurl.com` → extracts `newurl.com`

**Link Text Patterns:**
- `"Get in touch"` → extracts `Get in touch`
- `'Contact us'` → extracts `Contact us`
- `in 'Support' link` → extracts `Support`

---

## ⚙️ Advanced Usage

### Using Variables in JavaScript

You can use variables in `playwright_evaluate` scripts:

```json
{
  "tool": "playwright_evaluate",
  "params": {
    "script": "() => { const assetId = '{{asset_id}}'; const links = []; document.querySelectorAll('a[href]').forEach((a, i) => { links.push({ index: i, href: a.href, assetId: assetId }); }); return { totalLinks: links.length, links: links }; }"
  }
}
```

### Variables in Selectors

```json
{
  "tool": "playwright_click",
  "params": {
    "selector": "[data-asset-id='{{asset_id}}']"
  }
}
```

### Variables in Conditions

```json
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input[placeholder*='{{link_text}}']",
    "value": "{{new_url}}"
  }
}
```

---

## 🔧 Creating Variable-Based MDC Files

### Template Structure

```mcp
# Automation Name

**Description:** Brief description mentioning {{variable1}} and {{variable2}}

## Variables Required:
- `{{variable1}}` - Description (e.g., asset ID)
- `{{variable2}}` - Description (e.g., new URL)
- `{{variable3}}` - Optional description

## Keywords
keywords, for, search, matching

---

## Your automation steps using {{variables}}

### Step 1: Do something with {{variable1}}
{
  "tool": "playwright_navigate",
  "params": {
    "url": "https://example.com/{{variable1}}"
  }
}
```

```mcp
### Step 2: Do something with {{variable2}}
{
  "tool": "playwright_fill",
  "params": {
    "selector": "input",
    "value": "{{variable2}}"
  }
}
```

---

## 🚨 Important Notes

### Variable Names
- Use **lowercase with underscores**: `{{asset_id}}`, `{{new_url}}`
- **NOT**: `{{AssetId}}`, `{{NEW-URL}}`, `{{asset.id}}`

### Unsubstituted Variables
If a variable isn't found in the prompt, it remains as `{{variable}}` in the command and may cause errors.

**Tip:** Provide default values or make variables optional in your automation logic.

### Escaping Curly Braces
If you need literal `{{text}}` in your MDC file (not as a variable), currently it will be treated as a variable. Wrap it in quotes or use a different notation.

---

## 📊 Debugging Variables

### Check Extraction Logs

When running automation, check the console output:

```
[Variable Substitution] {{asset_id}} -> 3934720
[Variable Substitution] {{new_url}} -> www.autodesk.com/uk/support
[Variable Substitution] Warning: Unsubstituted variables found: ['{{link_text}}']
```

### Manual Testing

Test variable extraction from command line:

```bash
node mdc_executor.js your-file.mdc --context '{"variables": {"asset_id": "123", "new_url": "example.com"}}'
```

---

## 🎯 Example Prompts That Work

### Draftr Automation:
✅ "run draftr updater on asset 3934720 and change link to www.autodesk.com/uk/support"
✅ "update draftr asset 123456 link to example.com"
✅ "draftr updater asset=789012 url=test.com/page"
✅ "change link in draftr 555666 to newurl.com"

### Custom Automation:
✅ "run test with id=ABC123 and value=XYZ"
✅ "execute automation for user 456 with email test@example.com"

---

## 💡 Best Practices

### 1. Document Required Variables
Always list required variables at the top of your MDC file

### 2. Use Descriptive Names
- Good: `{{asset_id}}`, `{{new_url}}`, `{{user_email}}`
- Bad: `{{x}}`, `{{temp}}`, `{{data1}}`

### 3. Provide Examples
Include example prompts in your MDC file comments

### 4. Handle Missing Variables
Consider what happens if a variable isn't provided

### 5. Test Extraction
Test your prompt patterns to ensure variables are extracted correctly

---

## 🔗 Related Files

- **Example Template:** `mdc_files/draftr-link-updater.mdc`
- **Hardcoded Version:** `mdc_files/draftr-link-updater-automation.mdc`
- **Executor Code:** `mdc_executor.js` (substituteVariables method)
- **Extraction Logic:** `app.py` (_extract_variables_fallback method)

---

## 🚀 Quick Start

1. **Copy an existing MDC file**
2. **Replace hardcoded values with `{{variables}}`**
3. **Add a "Variables Required" section at the top**
4. **Test with a natural language prompt**
5. **Check logs to verify variable substitution**

---

## ✅ Summary

| Feature | Status |
|---------|--------|
| Variable syntax | `{{variable_name}}` |
| AI extraction | ✅ Enabled |
| Regex fallback | ✅ Enabled |
| Works in all params | ✅ Yes |
| Works in JavaScript | ✅ Yes |
| Case sensitive | ✅ Use lowercase_underscore |
| Error handling | ⚠️ Logs warnings for unsubstituted |

---

🎉 **You can now create ONE MDC file and reuse it for infinite variations!**

