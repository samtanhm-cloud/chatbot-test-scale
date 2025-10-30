#!/usr/bin/env node

/**
 * Cookie Injection Helper
 * Generates a browser_evaluate script to inject cookies from saved session
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sessionFile = path.join(__dirname, 'auth', 'draftr-session.json');

if (!fs.existsSync(sessionFile)) {
    console.error('❌ Session file not found:', sessionFile);
    console.error('Run: node setup_draftr_auth.js');
    process.exit(1);
}

const sessionData = JSON.parse(fs.readFileSync(sessionFile, 'utf-8'));
const cookies = sessionData.cookies || [];

console.log(`Found ${cookies.length} cookies in session file`);
console.log('\nGenerated cookie injection script:');
console.log('==========================================\n');

// Generate the injection function
const injectionScript = `async () => {
    // Cookie data from saved session
    const cookies = ${JSON.stringify(cookies, null, 2)};
    
    // Inject each cookie
    for (const cookie of cookies) {
        try {
            // Build cookie string
            let cookieStr = \`\${cookie.name}=\${cookie.value}\`;
            if (cookie.domain) cookieStr += \`; domain=\${cookie.domain}\`;
            if (cookie.path) cookieStr += \`; path=\${cookie.path}\`;
            if (cookie.expires) {
                const expiresDate = new Date(cookie.expires * 1000);
                cookieStr += \`; expires=\${expiresDate.toUTCString()}\`;
            }
            if (cookie.secure) cookieStr += '; secure';
            if (cookie.httpOnly) cookieStr += '; httponly';
            if (cookie.sameSite) cookieStr += \`; samesite=\${cookie.sameSite}\`;
            
            document.cookie = cookieStr;
        } catch (err) {
            console.error('Failed to set cookie:', cookie.name, err);
        }
    }
    
    // Verify cookies were set
    const setCookies = document.cookie.split(';').length;
    return {
        success: true,
        attempted: cookies.length,
        currentCookies: setCookies,
        message: \`Injected \${cookies.length} cookies, \${setCookies} total cookies now in browser\`
    };
}`;

console.log('Use this in your MDC file:');
console.log('```mcp');
console.log('{');
console.log('  "tool": "playwright_evaluate",');
console.log('  "params": {');
console.log(`    "script": "${injectionScript.replace(/\n/g, '\\n').replace(/"/g, '\\"')}"`);
console.log('  }');
console.log('}');
console.log('```\n');

console.log('Or save to file:');
const outputFile = path.join(__dirname, 'cookie-injection.json');
fs.writeFileSync(outputFile, JSON.stringify({
    tool: 'playwright_evaluate',
    params: {
        script: injectionScript
    }
}, null, 2));

console.log(`✅ Saved to: ${outputFile}`);

