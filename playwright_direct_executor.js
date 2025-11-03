#!/usr/bin/env node

/**
 * Direct Playwright Executor - For Local Testing with Visible Browser
 * Executes MDC files using direct Playwright API instead of MCP server
 * This bypasses MCP server's headless limitation
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PlaywrightDirectExecutor {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
    }

    async executeMDC(mdcFilePath, variables = {}) {
        console.log('[Direct Playwright] Starting execution...');
        console.log('[Direct Playwright] MDC File:', mdcFilePath);
        console.log('[Direct Playwright] Variables:', variables);
        
        try {
            // Read and parse MDC file
            let mdcContent = fs.readFileSync(mdcFilePath, 'utf-8');
            
            // Substitute variables
            for (const [key, value] of Object.entries(variables)) {
                const placeholder = `{{${key}}}`;
                mdcContent = mdcContent.replace(new RegExp(placeholder, 'g'), value);
                console.log(`[Variable] ${placeholder} -> ${value}`);
            }
            
            // Parse commands from MDC
            const commands = this.parseMDCCommands(mdcContent);
            console.log(`[Direct Playwright] Parsed ${commands.length} commands\n`);
            
            // Launch browser
            await this.launchBrowser();
            
            // Execute commands
            const results = [];
            for (let i = 0; i < commands.length; i++) {
                const cmd = commands[i];
                console.log(`[Command ${i + 1}/${commands.length}] ${cmd.tool}`);
                
                const startTime = Date.now();
                const result = await this.executeCommand(cmd);
                const duration = Date.now() - startTime;
                
                results.push({
                    success: true,
                    tool: cmd.tool,
                    output: result,
                    duration,
                    timestamp: new Date().toISOString()
                });
                
                console.log(`✅ Success (${duration}ms)\n`);
            }
            
            // Close browser
            await this.closeBrowser();
            
            return {
                success: true,
                total_commands: commands.length,
                successful: commands.length,
                failed: 0,
                results,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error('❌ Error:', error.message);
            await this.closeBrowser();
            
            return {
                success: false,
                error: error.message,
                stack: error.stack
            };
        }
    }
    
    async launchBrowser() {
        // Platform detection
        const isLinux = process.platform === 'linux';
        
        console.log(`[Browser] Launching ${isLinux ? 'Chromium' : 'Chrome'} (VISIBLE mode)...`);
        console.log(`[Browser] Platform: ${process.platform}`);
        
        const launchOptions = isLinux ? {
            // Linux: Use Chromium (bundled with Playwright)
            headless: false,
            slowMo: 100,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        } : {
            // macOS/Windows: Use Chrome via channel
            channel: 'chrome',
            headless: false,
            slowMo: 100,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        };
        
        this.browser = await chromium.launch(launchOptions);
        console.log(`✅ ${isLinux ? 'Chromium' : 'Chrome'} launched (VISIBLE)\n`);
        
        // Try to load saved authentication
        const authFile = path.join(__dirname, 'auth', 'draftr-session.json');
        try {
            if (fs.existsSync(authFile)) {
                this.context = await this.browser.newContext({
                    storageState: authFile
                });
                console.log('✅ Loaded authentication from:', authFile);
            } else {
                console.log('⚠️  No saved authentication found');
                this.context = await this.browser.newContext();
            }
        } catch (error) {
            console.log('⚠️  Could not load authentication:', error.message);
            this.context = await this.browser.newContext();
        }
        
        this.page = await this.context.newPage();
        console.log('✅ Browser ready\n');
    }
    
    async closeBrowser() {
        if (this.browser) {
            console.log('[Browser] Closing...');
            await this.browser.close();
            console.log('✅ Browser closed\n');
        }
    }
    
    async executeCommand(cmd) {
        const { tool, params } = cmd;
        
        switch (tool) {
            case 'playwright_navigate':
                await this.page.goto(params.url);
                return `Navigated to ${params.url}`;
                
            case 'playwright_screenshot':
                const timestamp = new Date().toISOString().replace(/:/g, '-').split('.')[0];
                const screenshotPath = path.join(__dirname, 'screenshots', `${params.name || 'screenshot'}-${timestamp}.png`);
                fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
                await this.page.screenshot({ path: screenshotPath, fullPage: true });
                return `Screenshot saved to: ${screenshotPath}`;
                
            case 'playwright_evaluate':
                // This WILL show alerts because browser is visible!
                const evalResult = await this.page.evaluate(eval(`(${params.script})`));
                return typeof evalResult === 'object' ? JSON.stringify(evalResult) : String(evalResult);
                
            case 'playwright_get_visible_text':
                const text = await this.page.textContent('body');
                return text;
                
            case 'playwright_click':
                await this.page.click(params.selector);
                return `Clicked: ${params.selector}`;
                
            case 'playwright_fill':
                await this.page.fill(params.selector, params.value);
                return `Filled: ${params.selector}`;
                
            default:
                console.log(`⚠️  Unsupported tool: ${tool}`);
                return `Skipped: ${tool} (not implemented in direct mode)`;
        }
    }
    
    parseMDCCommands(mdcContent) {
        const commands = [];
        const lines = mdcContent.split('\n');
        let inCodeBlock = false;
        let currentBlock = '';
        
        for (const line of lines) {
            if (line.trim() === '```mcp') {
                inCodeBlock = true;
                currentBlock = '';
            } else if (line.trim() === '```' && inCodeBlock) {
                inCodeBlock = false;
                try {
                    const parsed = JSON.parse(currentBlock);
                    commands.push(parsed);
                } catch (e) {
                    console.warn('[Parser] Failed to parse command:', e.message);
                }
            } else if (inCodeBlock) {
                currentBlock += line + '\n';
            }
        }
        
        return commands;
    }
}

// Main execution
if (import.meta.url === `file://${process.argv[1]}`) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: node playwright_direct_executor.js <mdc_file> [--context \'{"variables":{}}\']');
        process.exit(1);
    }
    
    const mdcFile = args[0];
    let context = { variables: {} };
    
    // Parse context if provided
    const contextIndex = args.indexOf('--context');
    if (contextIndex !== -1 && args[contextIndex + 1]) {
        try {
            context = JSON.parse(args[contextIndex + 1]);
        } catch (e) {
            console.error('Failed to parse context:', e.message);
            process.exit(1);
        }
    }
    
    const executor = new PlaywrightDirectExecutor();
    executor.executeMDC(mdcFile, context.variables || {})
        .then(result => {
            console.log('\n' + '='.repeat(60));
            console.log(result.success ? '✅ AUTOMATION COMPLETED' : '❌ AUTOMATION FAILED');
            console.log('='.repeat(60));
            console.log(JSON.stringify(result, null, 2));
            process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
            console.error('Fatal error:', error);
            process.exit(1);
        });
}

export default PlaywrightDirectExecutor;

