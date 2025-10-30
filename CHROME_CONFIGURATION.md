# 🌐 Chrome Browser Configuration

## Overview

The streamlit_mdc_app has been configured to use **Google Chrome** instead of Chromium for Playwright browser automation.

## What Changed?

### 1. Browser Channel Configuration (`playwright-mcp-config.json`)

```json
{
  "browser": {
    "channel": "chrome",  // ← Changed from default (chromium)
    "headless": true,
    "args": [...]
  },
  "launchOptions": {
    "channel": "chrome",  // ← Added here too
    "headless": true,
    "args": [...]
  }
}
```

### 2. Installation Script (`setup_dependencies.sh`)

```bash
# Changed from: npx playwright install chromium
npx playwright install chrome  // ← Now installs Chrome
```

### 3. App Installation (`app.py`)

```python
# Installation commands now use 'chrome' instead of 'chromium'
'cmd': ['npx', 'playwright-core', 'install', 'chrome']
```

## Why Chrome Instead of Chromium?

### Advantages of Chrome:
1. **Better compatibility** - Chrome is more widely tested
2. **System integration** - Uses your system's Chrome installation (when available)
3. **Automatic updates** - Chrome updates with your system
4. **Better plugin support** - Some extensions work better with Chrome
5. **Industry standard** - More closely matches production environments

### Chromium vs Chrome:
- **Chromium**: Open-source browser, base for Chrome
- **Chrome**: Google's branded version with additional features

## How It Works

### Local Development
When you run `npx playwright install chrome`, Playwright will:
1. Check if Google Chrome is installed on your system
2. Use the system Chrome if available
3. Download Playwright's Chrome build if system Chrome is not found

### Cloud Deployment (Streamlit Cloud)
On Streamlit Cloud, Playwright will:
1. Download and install the Chrome browser
2. Run it in headless mode (no GUI)
3. Use the configuration from `playwright-mcp-config.json`

## Verification

### Check if Chrome is Configured

1. **In the App UI:**
   - Look for "Playwright Chrome: 🟢 Ready" in System Status
   - Expand "Browser Configuration Check" to see details

2. **Command Line:**
   ```bash
   # Check if Chrome is installed
   npx playwright install --dry-run chrome
   
   # Expected output: "chrome is already installed"
   ```

3. **Config File:**
   ```bash
   cat playwright-mcp-config.json | grep channel
   
   # Expected output: "channel": "chrome",
   ```

## Switching Back to Chromium

If you need to switch back to Chromium:

### 1. Update `playwright-mcp-config.json`
```json
{
  "browser": {
    // Remove "channel": "chrome",
    "headless": true,
    ...
  }
}
```

### 2. Update `setup_dependencies.sh`
```bash
npx playwright install chromium
```

### 3. Update `app.py`
Change all `'chrome'` back to `'chromium'` in install commands.

### 4. Reinstall
```bash
rm .playwright_installed
npm run setup  # or click "Force Reinstall" in the app
```

## Troubleshooting

### Issue: "Chrome not found"

**Solution 1: Install Chrome locally**
```bash
# macOS
brew install --cask google-chrome

# Linux (Ubuntu/Debian)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

**Solution 2: Let Playwright download Chrome**
```bash
npx playwright install chrome
```

### Issue: "Channel 'chrome' not supported"

This means your Playwright version is too old. Update:
```bash
npm install -D @playwright/test@latest
npx playwright install chrome
```

### Issue: Still using Chromium

Check your configuration:
```bash
# 1. Verify config file
cat playwright-mcp-config.json

# 2. Clear cache
rm -rf node_modules/.cache/ms-playwright/

# 3. Reinstall
npx playwright install chrome
```

## Environment Variables

The app sets these environment variables for Chrome:

```bash
PLAYWRIGHT_HEADLESS=1              # Force headless mode
PLAYWRIGHT_CHROMIUM_NO_SANDBOX=1   # Disable sandbox (cloud)
PLAYWRIGHT_BROWSERS_PATH=0         # Use local installation
BROWSER_HEADLESS=true              # Generic headless flag
```

Note: `PLAYWRIGHT_CHROMIUM_NO_SANDBOX` applies to both Chromium and Chrome.

## Browser Arguments

Chrome runs with these arguments:

```javascript
[
  "--headless=new",              // New headless mode
  "--no-sandbox",                // Required for cloud
  "--disable-setuid-sandbox",    // Security bypass for cloud
  "--disable-dev-shm-usage",     // Use /tmp instead of /dev/shm
  "--disable-background-networking",
  "--disable-default-apps",
  "--no-first-run",
  "--disable-features=TranslateUI"
]
```

## Performance

### Chrome vs Chromium Performance:
- **Startup time**: Similar (~2-3 seconds)
- **Memory usage**: Similar (~150-200 MB)
- **Execution speed**: Identical (same engine)

The main difference is compatibility and features, not performance.

## Security

### Security Flags for Cloud Deployment:

```javascript
args: [
  "--no-sandbox",              // Required for containerized environments
  "--disable-setuid-sandbox"   // Required when running as non-root
]
```

⚠️ **Note:** These flags reduce security but are necessary for cloud environments where you don't have full system privileges.

## Browser Detection in MDC Files

Your MDC automation files don't need to change. They'll automatically use Chrome:

```mcp
{
  "tool": "browser_navigate",
  "params": { "url": "https://example.com" }
}
```

Playwright will launch Chrome automatically based on the configuration.

## System Requirements

### Local Development:
- Node.js 16+
- 200 MB free disk space (for Chrome binary)
- Supported OS: macOS, Linux, Windows

### Cloud Deployment:
- Streamlit Cloud automatically provides all dependencies
- Chrome is downloaded during installation (~100 MB)

## Summary

✅ **Changed:** Browser from Chromium to Chrome  
✅ **Benefit:** Better compatibility and system integration  
✅ **Impact:** No changes needed to your MDC files  
✅ **Configuration:** `playwright-mcp-config.json` + `setup_dependencies.sh`

---

**For more information:**
- [Playwright Browsers](https://playwright.dev/docs/browsers)
- [Chrome for Testing](https://developer.chrome.com/blog/chrome-for-testing/)
- [Playwright Configuration](https://playwright.dev/docs/test-configuration)

