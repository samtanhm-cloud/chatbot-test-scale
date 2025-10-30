#!/usr/bin/env node

/**
 * Cookie Capture Script for Draftr Authentication
 * 
 * This script:
 * 1. Opens a real browser window
 * 2. Navigates to Draftr
 * 3. Waits for you to log in manually
 * 4. Captures session cookies
 * 5. Outputs them in format for Streamlit secrets
 * 
 * Usage:
 *   node capture-cookies.js
 */

import { chromium } from 'playwright';

async function captureCookies() {
    console.log('🚀 Starting Cookie Capture...\n');
    console.log('📋 Instructions:');
    console.log('   1. A browser window will open');
    console.log('   2. Log in to Draftr manually (use SSO/2FA as normal)');
    console.log('   3. Wait until you see the Draftr asset page');
    console.log('   4. Press ENTER in this terminal when logged in\n');
    
    // Launch browser in NON-headless mode
    const browser = await chromium.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Navigate to Draftr
    console.log('🌐 Navigating to Draftr...\n');
    await page.goto('https://webpub.autodesk.com/draftr/');
    
    // Wait for user to log in
    console.log('⏸️  PAUSED - Please log in to Draftr now');
    console.log('Press ENTER when you are logged in and see the Draftr homepage...\n');
    
    // Wait for user input
    await new Promise(resolve => {
        process.stdin.once('data', () => resolve());
    });
    
    // Capture cookies
    console.log('\n📸 Capturing cookies...');
    const cookies = await context.cookies();
    
    // Filter relevant cookies (only from draftr domain)
    const draftrCookies = cookies.filter(cookie => 
        cookie.domain.includes('draftr') || 
        cookie.domain.includes('autodesk')
    );
    
    console.log(`✅ Captured ${draftrCookies.length} cookies\n`);
    
    // Output in format for Streamlit secrets
    console.log('=' .repeat(60));
    console.log('📋 COPY THIS TO YOUR STREAMLIT SECRETS:');
    console.log('=' .repeat(60));
    console.log('\nIn Streamlit Cloud:');
    console.log('1. Go to app settings');
    console.log('2. Click "Secrets"');
    console.log('3. Add this:\n');
    
    console.log('# Draftr Authentication Cookies');
    console.log('DRAFTR_COOKIES = """');
    console.log(JSON.stringify(draftrCookies, null, 2));
    console.log('"""\n');
    
    console.log('=' .repeat(60));
    console.log('🔐 SECURITY NOTES:');
    console.log('=' .repeat(60));
    console.log('- These cookies give access to your Draftr account');
    console.log('- Store them ONLY in Streamlit secrets (encrypted)');
    console.log('- DO NOT commit them to git');
    console.log('- DO NOT share them');
    console.log('- Cookies will expire - recapture when authentication fails\n');
    
    console.log('=' .repeat(60));
    console.log('✅ COOKIE CAPTURE COMPLETE');
    console.log('=' .repeat(60));
    
    await browser.close();
}

// Run
captureCookies().catch(console.error);

