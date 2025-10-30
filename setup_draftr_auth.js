#!/usr/bin/env node
/**
 * Draftr Authentication Setup - Persistent Browser Session
 * 
 * This script helps you log in to Draftr ONCE, then saves the browser session
 * so all future automation runs are already authenticated.
 * 
 * NO TOKEN CAPTURE NEEDED! NO SECRETS NEEDED!
 * 
 * Usage:
 *   node setup_draftr_auth.js
 * 
 * What it does:
 * 1. Opens a VISIBLE browser
 * 2. Navigates to Draftr
 * 3. You log in manually (SSO/2FA works!)
 * 4. Saves the entire browser session to a file
 * 5. All future automation runs reuse this logged-in session!
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Where to save the authenticated session
const AUTH_DIR = path.join(__dirname, 'auth');
const SESSION_FILE = path.join(AUTH_DIR, 'draftr-session.json');

async function main() {
    console.log('=' .repeat(70));
    console.log('🔐 Draftr Authentication Setup');
    console.log('=' .repeat(70));
    console.log();
    console.log('This will help you log in to Draftr ONCE.');
    console.log('The browser session will be saved and reused for all automation.');
    console.log();
    console.log('✅ SSO/2FA supported');
    console.log('✅ No token extraction needed');
    console.log('✅ No secrets to manage');
    console.log('✅ Works exactly like manual login');
    console.log();
    console.log('=' .repeat(70));
    console.log();
    
    // Create auth directory if it doesn't exist
    if (!fs.existsSync(AUTH_DIR)) {
        fs.mkdirSync(AUTH_DIR, { recursive: true });
        console.log('✅ Created auth directory:', AUTH_DIR);
    }
    
    // Check if session already exists
    if (fs.existsSync(SESSION_FILE)) {
        console.log('⚠️  Existing session found:', SESSION_FILE);
        console.log();
        console.log('Options:');
        console.log('  1. Delete it and create new session (press ENTER)');
        console.log('  2. Keep existing session (press Ctrl+C)');
        console.log();
        
        await new Promise(resolve => {
            process.stdin.once('data', () => {
                fs.unlinkSync(SESSION_FILE);
                console.log('✅ Deleted old session');
                console.log();
                resolve();
            });
        });
    }
    
    console.log('🚀 Launching Chrome browser...');
    console.log();
    
    // Launch Chrome browser in VISIBLE mode
    const browser = await chromium.launch({
        channel: 'chrome',  // Use Chrome instead of Chromium
        headless: false,    // VISIBLE so you can log in
        slowMo: 100         // Slightly slower for better visibility
    });
    
    // Create context WITHOUT saved state (fresh login)
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Navigate to Draftr login page
    console.log('🌐 Navigating to Draftr...');
    await page.goto('https://webpub.autodesk.com/draftr/asset/3934720');
    
    console.log();
    console.log('=' .repeat(70));
    console.log('⏸️  PLEASE LOG IN NOW');
    console.log('=' .repeat(70));
    console.log();
    console.log('1. Complete the Autodesk login in the browser');
    console.log('2. SSO and 2FA will work as normal');
    console.log('3. Wait until you see the Draftr asset page fully loaded');
    console.log('4. Make sure you can see the email content');
    console.log('5. Then press ENTER here in the terminal');
    console.log();
    
    // Wait for user to log in
    await new Promise(resolve => {
        process.stdin.once('data', () => resolve());
    });
    
    console.log();
    console.log('💾 Saving browser session...');
    
    // Save the entire browser state (cookies, localStorage, sessionStorage, etc.)
    const state = await context.storageState();
    fs.writeFileSync(SESSION_FILE, JSON.stringify(state, null, 2));
    
    console.log('✅ Session saved to:', SESSION_FILE);
    console.log();
    
    // Show statistics
    const cookies = state.cookies || [];
    const origins = state.origins || [];
    
    console.log('=' .repeat(70));
    console.log('📊 Session Details:');
    console.log('=' .repeat(70));
    console.log(`   Cookies saved: ${cookies.length}`);
    console.log(`   Domains: ${[...new Set(cookies.map(c => c.domain))].join(', ')}`);
    console.log(`   Storage origins: ${origins.length}`);
    console.log();
    
    if (cookies.length < 3) {
        console.log('⚠️  WARNING: Very few cookies saved!');
        console.log('   Make sure you are fully logged in and the page loaded completely.');
        console.log('   You may want to run this script again.');
        console.log();
    }
    
    await browser.close();
    
    console.log('=' .repeat(70));
    console.log('✅ SETUP COMPLETE!');
    console.log('=' .repeat(70));
    console.log();
    console.log('🎯 What Happens Next:');
    console.log();
    console.log('1. All automation runs will use this logged-in session');
    console.log('2. You won\'t need to log in again');
    console.log('3. Browser will "remember" you\'re authenticated');
    console.log('4. No tokens or secrets needed!');
    console.log();
    console.log('📝 Notes:');
    console.log('   - Session persists until you log out or password changes');
    console.log('   - If automation shows "login required", re-run this script');
    console.log('   - Session file location: ' + SESSION_FILE);
    console.log();
    console.log('🚀 Ready to run automation!');
    console.log();
}

main().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
});

