# Quick Reference Card 📇

## 🎯 Three Prompt Formats - At a Glance

---

### Format 1️⃣: Change Specific Link

**When:** Update ONE link by its text

**Format:**
```
run mdc on https://webpub.autodesk.com/draftr/asset/<ID> and change link in "<text>" to "<URL>"
```

**Example:**
```
run mdc on https://webpub.autodesk.com/draftr/asset/3934720 and change link in "Get in touch" to "www.autodesk.com/uk/support"
```

**Extracts:** `asset_id`, `link_text`, `new_url`

---

### Format 2️⃣: Replace All Matching URLs

**When:** Update ALL links with same URL pattern

**Format:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/<ID> to replace all "<old_url>" links to "<new_url>"
```

**Example:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all "oldsite.com" links to "newsite.com"
```

**Extracts:** `asset_id`, `old_url`, `new_url`

---

### Format 3️⃣: Replace Domain Paths

**When:** Update ALL links with specific domain/path

**Format:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/<ID> to replace all domain "<old_domain>" links to "<new_domain>"
```

**Example:**
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/3934720 to replace all domain "/en/" links to "/uk/"
```

**Extracts:** `asset_id`, `old_domain`, `new_domain`

---

## 📋 Variable Reference

| Variable | Format 1 | Format 2 | Format 3 | Description |
|----------|----------|----------|----------|-------------|
| `{{asset_id}}` | ✅ | ✅ | ✅ | Draftr asset ID |
| `{{link_text}}` | ✅ | ❌ | ❌ | Anchor text to find |
| `{{new_url}}` | ✅ | ✅ | ❌ | New URL destination |
| `{{old_url}}` | ❌ | ✅ | ❌ | Old URL pattern |
| `{{old_domain}}` | ❌ | ❌ | ✅ | Old domain/path |
| `{{new_domain}}` | ❌ | ❌ | ✅ | New domain/path |
| `{{operation}}` | ✅ | ✅ | ✅ | Operation type |

---

## 🚀 Copy & Paste Templates

### Template 1: Specific Link
```
run mdc on https://webpub.autodesk.com/draftr/asset/[ASSET_ID] and change link in "[LINK_TEXT]" to "[NEW_URL]"
```

### Template 2: Bulk Replace
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/[ASSET_ID] to replace all "[OLD_URL]" links to "[NEW_URL]"
```

### Template 3: Domain Swap
```
run mdc on URL https://webpub.autodesk.com/draftr/asset/[ASSET_ID] to replace all domain "[OLD_DOMAIN]" links to "[NEW_DOMAIN]"
```

---

## ⚡ Common Use Cases

| Task | Use Format | Example |
|------|-----------|---------|
| Update CTA button | **1** | Change "Learn More" to new landing page |
| Site migration | **2** | Replace all old.com with new.com |
| Locale change | **3** | Replace /en/ with /uk/ |
| Fix broken link | **1** | Change specific link by text |
| Rebrand | **2** | Replace all brand URLs |
| Region switch | **3** | Replace /us/ with /ca/ |

---

## 🎓 Tips

✅ **Always use quotes** around text and URLs
✅ **Include full Draftr URL** with asset ID
✅ **Double-check** asset ID exists
✅ **Match exact** link text for Format 1
✅ **Use domain paths** with slashes for Format 3

❌ **Don't forget** quotes around values
❌ **Don't mix** formats in one prompt
❌ **Don't omit** the asset ID

---

## 🔗 Full Documentation

- **Complete Guide:** `PROMPT_FORMATS.md`
- **Variable System:** `VARIABLE_SUBSTITUTION_GUIDE.md`
- **Tool Reference:** `ACTUAL_MCP_TOOLS.md`

---

**Ready to automate? Just pick a format and go!** 🚀

