# Supported Prompt Formats 📝

Complete guide to all supported prompt formats for Draftr automation.

---

## 📋 Three Main Formats

### Format 1: Change Specific Link (by text)
**Use when:** You want to change ONE specific link identified by its anchor text

**Pattern:**
```
run mdc on https://webpub.autodesk.com/draftr/asset/<assetID> and change link in "<text>" to "<New Link>"
```

**Examples:**
```
run mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"

run mdc on https://webpub.autodesk.com/draftr/asset/123456 and change link in "Contact Us" to "support.example.com/contact"

run mdc on https://webpub.autodesk.com/draftr/asset/789012 and change link in "Learn More" to "www.company.com/learn"
```

**Extracted Variables:**
- `asset_id`: 3934720
- `link_text`: "Get in touch"
- `new_url`: "www.autodesk.com/uk/support"
- `operation`: "change_specific"

---

### Format 2: Replace All Matching Links (by URL pattern)
**Use when:** You want to replace ALL links that match a certain URL pattern

**Pattern:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/<assetID> to replace all "<Links to replace>" links to "<new links>"
```

**Examples:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all "oldsite.com" links to "newsite.com"

run mdc on URL https://webpub.autodesk.com/draftr/asset/123456 to replace all "support.old.com" links to "help.new.com"

run mdc on URL https://webpub.autodesk.com/draftr/asset/789012 to replace all "company.com/old-page" links to "company.com/new-page"
```

**Extracted Variables:**
- `asset_id`: 3934720
- `old_url`: "oldsite.com"
- `new_url`: "newsite.com"
- `operation`: "replace_all"

---

### Format 3: Replace All Links with Specific Domain (domain swap)
**Use when:** You want to replace ALL links containing a specific domain path (like /en/, /uk/, etc.)

**Pattern:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/<assetID> to replace all domain "<insert domain like /en/ etc>" links to "<new domain>"
```

**Examples:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all domain "/en/" links to "/uk/"

run mdc on URL https://webpub.autodesk.com/draftr/asset/123456 to replace all domain "/us/" links to "/ca/"

run mdc on URL https://webpub.autodesk.com/draftr/asset/789012 to replace all domain "/products/old/" links to "/products/new/"
```

**Extracted Variables:**
- `asset_id`: 3934720
- `old_domain`: "/en/"
- `new_domain`: "/uk/"
- `operation`: "replace_domain"

---

## 🎯 Quick Comparison

| Format | Use Case | Identifies Links By | Changes |
|--------|----------|---------------------|---------|
| **Format 1** | Single specific link | Anchor text | One link |
| **Format 2** | Multiple links | URL pattern | All matching |
| **Format 3** | Domain migration | Domain/path | All matching |

---

## 🔍 Detailed Breakdown

### Format 1: Change Specific Link

#### What it does:
- Finds the link with matching anchor text (e.g., "Get in touch")
- Changes ONLY that specific link's URL
- Ignores all other links

#### Best for:
- ✅ Updating a primary CTA button
- ✅ Fixing a specific broken link
- ✅ Changing one call-to-action URL
- ✅ When you know the exact link text

#### Variables Used:
```json
{
  "asset_id": "3934720",
  "link_text": "Get in touch",
  "new_url": "www.autodesk.com/uk/support",
  "operation": "change_specific"
}
```

---

### Format 2: Replace All Matching Links

#### What it does:
- Finds ALL links containing the old URL pattern
- Replaces each one with the new URL
- Can be partial match (e.g., "oldsite.com" matches "https://oldsite.com/any/path")

#### Best for:
- ✅ Migrating from old domain to new domain
- ✅ Updating multiple instances of same link
- ✅ Bulk URL replacement
- ✅ Site rebranding

#### Variables Used:
```json
{
  "asset_id": "3934720",
  "old_url": "oldsite.com",
  "new_url": "newsite.com",
  "operation": "replace_all"
}
```

---

### Format 3: Replace Domain Paths

#### What it does:
- Finds ALL links containing the old domain path (e.g., "/en/")
- Replaces the domain portion with the new domain path
- Preserves the rest of the URL structure

#### Best for:
- ✅ Language/locale switching (en → uk, us → ca)
- ✅ Path migrations (old-section → new-section)
- ✅ Regional content updates
- ✅ Internationalization changes

#### Variables Used:
```json
{
  "asset_id": "3934720",
  "old_domain": "/en/",
  "new_domain": "/uk/",
  "operation": "replace_domain"
}
```

---

## 💡 Tips & Best Practices

### 1. Asset ID
- **Always required** in all formats
- Extract from Draftr URL: `https://webpub.autodesk.com/draftr/asset/3934720`
- Usually 6-7 digits

### 2. Using Quotes
- **Use double quotes** `"like this"` for text and URLs
- Alternative: Use angle brackets `<like this>`
- **Don't mix**: Pick one style and stick with it

### 3. URL Format
- Include full URL or just domain: both work
  - ✅ `https://www.example.com/path`
  - ✅ `www.example.com/path`
  - ✅ `example.com`
  
### 4. Domain Paths
- Always include leading/trailing slashes: `/en/`
- Can be deeper paths: `/products/category/`
- Works with query params: `/path?lang=en`

---

## 🧪 Test Your Prompts

### Testing Format 1:
```bash
# Correct:
run mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"

# Also works:
run mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in <Get in touch> to <www.autodesk.com/uk/support>
```

### Testing Format 2:
```bash
# Correct:
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all "oldsite.com" links to "newsite.com"

# Also works:
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all <oldsite.com> links to <newsite.com>
```

### Testing Format 3:
```bash
# Correct:
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all domain "/en/" links to "/uk/"

# Also works:
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all domain </en/> links to </uk/>
```

---

## 🔧 Troubleshooting

### "No variables extracted"
**Problem:** System couldn't extract asset_id, urls, etc.

**Solution:**
- ✅ Make sure asset ID is in the URL
- ✅ Use quotes around text and URLs
- ✅ Follow exact format patterns
- ✅ Check spelling of keywords ("change", "replace", "domain")

### "Wrong operation detected"
**Problem:** System extracted variables but chose wrong operation type

**Solution:**
- ✅ Use "change link in" for Format 1
- ✅ Use "replace all" for Format 2
- ✅ Use "replace all domain" for Format 3

### "Asset not found"
**Problem:** Asset ID not extracted correctly

**Solution:**
- ✅ Use full Draftr URL with asset ID
- ✅ Make sure asset ID is 6-7 digits
- ✅ Check that URL is formatted correctly

---

## 📊 Variable Extraction Examples

### Example 1: Format 1
**Prompt:**
```
run mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"
```

**Extracted:**
```json
{
  "asset_id": "3934720",
  "link_text": "Get in touch",
  "new_url": "www.autodesk.com/uk/support",
  "operation": "change_specific"
}
```

**What MDC file sees:**
```
{{asset_id}} → 3934720
{{link_text}} → Get in touch
{{new_url}} → www.autodesk.com/uk/support
{{operation}} → change_specific
```

---

### Example 2: Format 2
**Prompt:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/123456 to replace all "support.old.com" links to "help.new.com"
```

**Extracted:**
```json
{
  "asset_id": "123456",
  "old_url": "support.old.com",
  "new_url": "help.new.com",
  "operation": "replace_all"
}
```

**What MDC file sees:**
```
{{asset_id}} → 123456
{{old_url}} → support.old.com
{{new_url}} → help.new.com
{{operation}} → replace_all
```

---

### Example 3: Format 3
**Prompt:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/789012 to replace all domain "/us/" links to "/ca/"
```

**Extracted:**
```json
{
  "asset_id": "789012",
  "old_domain": "/us/",
  "new_domain": "/ca/",
  "operation": "replace_domain"
}
```

**What MDC file sees:**
```
{{asset_id}} → 789012
{{old_domain}} → /us/
{{new_domain}} → /ca/
{{operation}} → replace_domain
```

---

## 🎓 Advanced Examples

### Combining with paths:
```
run mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Download" to "files.autodesk.com/downloads/product-v2.pdf"
```

### Multiple word link text:
```
run mdc on https://webpub.autodesk.com/draftr/asset/123456 and change link in "Contact Our Support Team" to "support.company.com/contact-form"
```

### Complex domain replacement:
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/789012 to replace all domain "/products/legacy/" links to "/products/current/"
```

---

## ✅ Checklist Before Running

- [ ] Asset ID is correct and exists in Draftr
- [ ] Used correct format (1, 2, or 3) for your use case
- [ ] Quoted all text and URLs properly
- [ ] Double-checked target URLs are correct
- [ ] Verified link text matches exactly (for Format 1)
- [ ] Confirmed old URL/domain pattern (for Formats 2 & 3)

---

## 🚀 Ready to Use!

All three formats are now fully supported. The system will:
1. ✅ Parse your prompt
2. ✅ Extract all variables
3. ✅ Load appropriate MDC template
4. ✅ Substitute variables
5. ✅ Execute automation
6. ✅ Return results

**Just type your prompt and go!** 🎉

