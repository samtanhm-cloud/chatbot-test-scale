#!/usr/bin/env node

/**
 * MDC Executor for Playwright MCP - REAL IMPLEMENTATION
 * Executes MDC files with actual Playwright browser automation via MCP SDK
 * Version: 2.0.0 - Production Ready (ES Module)
 */

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

// ES module equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class MDCExecutor {
    constructor() {
        this.mcpServerPath = process.env.MCP_SERVER_PATH || 'npx';
        
        // Check if running on cloud
        this.isCloud = process.env.STREAMLIT_RUNTIME_ENV === 'cloud' || 
                      fs.existsSync('/mount/src');
        
        // Build MCP server args with config file path
        const configPath = path.join(__dirname, 'playwright-mcp-config.json');
        
        if (process.env.MCP_SERVER_ARGS) {
            this.mcpServerArgs = process.env.MCP_SERVER_ARGS.split(' ');
        } else {
            // Try to pass config file if it exists
            if (fs.existsSync(configPath)) {
                this.mcpServerArgs = [
                    '-y',
                    '@executeautomation/playwright-mcp-server',
                    '--config',
                    configPath
                ];
                console.log(`[MDC Executor] Using config file: ${configPath}`);
            } else {
                this.mcpServerArgs = ['-y', '@executeautomation/playwright-mcp-server'];
            }
        }
        
        this.mcpClient = null;
        this.mcpServerProcess = null;
        
        console.log(`[MDC Executor] Running in ${this.isCloud ? 'cloud' : 'local'} mode`);
        console.log(`[MDC Executor] Headless mode forced: ${process.env.PLAYWRIGHT_HEADLESS}`);
    }

    async executeMDC(mdcFilePath, context = {}) {
        console.log(`[MDC Executor] Starting execution of: ${mdcFilePath}`);
        
        try {
            // Read MDC file
            const mdcContent = fs.readFileSync(mdcFilePath, 'utf-8');
            console.log(`[MDC Executor] Loaded MDC file (${mdcContent.length} bytes)`);
            
            // Parse MDC content and extract commands
            const commands = this.parseMDCCommands(mdcContent);
            console.log(`[MDC Executor] Parsed ${commands.length} commands`);
            
            if (commands.length === 0) {
                console.warn('[MDC Executor] Warning: No MCP commands found in file');
                return {
                    success: false,
                    error: 'No executable commands found in MDC file',
                    total_commands: 0,
                    successful: 0,
                    failed: 0,
                    results: []
                };
            }
            
            // Start MCP server and connect client
            console.log('[MDC Executor] Starting Playwright MCP server...');
            await this.startMCPConnection();
            
            // Execute commands sequentially
            const results = [];
            for (let i = 0; i < commands.length; i++) {
                console.log(`[MDC Executor] Executing command ${i + 1}/${commands.length}`);
                const result = await this.executeCommand(commands[i], context);
                results.push(result);
                
                // Log result
                console.log(`[MDC Executor] Command ${i + 1} result:`, 
                    result.success ? '✓ Success' : '✗ Failed');
                
                // Log detailed output if available
                if (result.output && typeof result.output === 'object') {
                    console.log(`[MDC Executor] Output:`, JSON.stringify(result.output, null, 2));
                }
                
                // Stop on critical failure
                if (!result.success && !commands[i].optional) {
                    console.error(`[MDC Executor] Critical command failed, stopping execution`);
                    console.error(`[MDC Executor] Error:`, result.error || 'No error message provided');
                    console.error(`[MDC Executor] Full result:`, JSON.stringify(result, null, 2));
                    if (result.fullError) {
                        console.error(`[MDC Executor] Full error object:`, result.fullError);
                    }
                    break;
                }
            }
            
            // Stop MCP server
            await this.stopMCPConnection();
            
            // Compile final results
            const summary = this.generateSummary(results);
            console.log('[MDC Executor] Execution completed');
            console.log(JSON.stringify(summary, null, 2));
            
            return summary;
            
        } catch (error) {
            console.error('[MDC Executor] Fatal error:', error);
            
            // Ensure cleanup
            await this.stopMCPConnection();
            
            return {
                success: false,
                error: error.message,
                stack: error.stack,
                total_commands: 0,
                successful: 0,
                failed: 0,
                results: []
            };
        }
    }

    parseMDCCommands(mdcContent) {
        /**
         * Parse MDC file format
         * Expected format:
         * ```mcp
         * {
         *   "tool": "browser_navigate",
         *   "params": { "url": "https://example.com" }
         * }
         * ```
         */
        const commands = [];
        const lines = mdcContent.split('\n');
        let inCodeBlock = false;
        let inMcpBlock = false;
        let currentCommand = '';
        let lineNumber = 0;
        
        for (const line of lines) {
            lineNumber++;
            const trimmed = line.trim();
            
            if (trimmed.startsWith('```')) {
                if (inCodeBlock) {
                    // End of code block
                    if (inMcpBlock) {
                        // Try to parse the MCP command
                        try {
                            const cmd = JSON.parse(currentCommand.trim());
                            if (cmd.tool) {
                                commands.push({
                                    ...cmd,
                                    _lineNumber: lineNumber
                                });
                            } else {
                                console.warn(`[MDC Parser] Line ${lineNumber}: Command missing 'tool' property`);
                            }
                        } catch (e) {
                            console.warn(`[MDC Parser] Line ${lineNumber}: Failed to parse command:`, e.message);
                        }
                        inMcpBlock = false;
                    }
                    currentCommand = '';
                    inCodeBlock = false;
                } else {
                    // Start of code block
                    inCodeBlock = true;
                    // Check if it's an MCP block
                    if (trimmed === '```mcp' || trimmed.startsWith('```mcp ')) {
                        inMcpBlock = true;
                    }
                }
            } else if (inCodeBlock && inMcpBlock) {
                currentCommand += line + '\n';
            }
        }
        
        return commands;
    }

    async startMCPConnection() {
        try {
            // Log what we're starting
            console.log(`[MCP Server] Starting: ${this.mcpServerPath} ${this.mcpServerArgs.join(' ')}`);
            
            // Ensure headless mode is set (critical for cloud environments)
            // Force multiple environment variables for maximum compatibility
            const launchOptions = {
                headless: true,
                args: [
                    '--headless',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--single-process',
                    '--no-zygote'
                ]
            };
            
            const env = {
                ...process.env,
                // Playwright-specific
                PLAYWRIGHT_HEADLESS: '1',
                PLAYWRIGHT_CHROMIUM_NO_SANDBOX: '1',
                // CRITICAL: Force local browser path (0 = use node_modules/.local-browsers/)
                PLAYWRIGHT_BROWSERS_PATH: '0',
                // Pass launch options as JSON (some MCP servers read this)
                PLAYWRIGHT_LAUNCH_OPTIONS: JSON.stringify(launchOptions),
                BROWSER_LAUNCH_OPTIONS: JSON.stringify(launchOptions),
                // Generic browser flags
                BROWSER_HEADLESS: 'true',
                HEADLESS: 'true',
                // Chromium-specific
                CHROME_HEADLESS: 'true',
                CHROMIUM_FLAGS: '--headless --no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --single-process',
                // Additional stability flags
                NO_SANDBOX: 'true',
                DISABLE_GPU: 'true'
            };
            
            console.log(`[MCP Server] Environment configured:`);
            console.log(`[MCP Server]   PLAYWRIGHT_HEADLESS: ${env.PLAYWRIGHT_HEADLESS}`);
            console.log(`[MCP Server]   PLAYWRIGHT_BROWSERS_PATH: ${env.PLAYWRIGHT_BROWSERS_PATH} (0=local)`);
            console.log(`[MCP Server]   PLAYWRIGHT_LAUNCH_OPTIONS: ${env.PLAYWRIGHT_LAUNCH_OPTIONS}`);
            console.log(`[MCP Server]   DISPLAY: ${env.DISPLAY || 'not set'}`);
            console.log(`[MCP Server]   NO_SANDBOX: ${env.NO_SANDBOX}`);
            console.log(`[MCP Server]   CHROMIUM_FLAGS: ${env.CHROMIUM_FLAGS}`);
            
            // Create MCP client
            this.mcpClient = new Client({
                name: 'mdc-executor',
                version: '2.0.0'
            }, {
                capabilities: {
                    tools: {}
                }
            });
            
            // Create transport (SDK will spawn and manage the process internally)
            const transport = new StdioClientTransport({
                command: this.mcpServerPath,
                args: this.mcpServerArgs,
                env: env  // Pass environment variables including headless config
            });
            
            // Connect the client
            await this.mcpClient.connect(transport);
            console.log('[MCP Server] Connected successfully');
            
            // List available tools
            const toolsList = await this.mcpClient.listTools();
            console.log(`[MCP Server] Available tools: ${toolsList.tools.length}`);
            
            // Show tool names if not too many
            if (toolsList.tools.length > 0 && toolsList.tools.length < 20) {
                toolsList.tools.forEach(tool => {
                    console.log(`[MCP Server]   - ${tool.name}`);
                });
            }
            
        } catch (error) {
            console.error('[MCP Server] Failed to start:', error.message);
            throw error;
        }
    }

    async stopMCPConnection() {
        console.log('[MCP Server] Stopping connection...');
        
        try {
            // Close MCP client
            if (this.mcpClient) {
                await this.mcpClient.close();
                this.mcpClient = null;
                console.log('[MCP Server] Client disconnected');
            }
            
            // No need to manually kill process - SDK handles it when client closes
        } catch (error) {
            console.error('[MCP Server] Error during shutdown:', error);
        }
    }

    async executeCommand(command, context) {
        /**
         * Execute a single MCP command using the real MCP SDK
         */
        console.log(`[Command Executor] Tool: ${command.tool}`);
        console.log(`[Command Executor] Params:`, JSON.stringify(command.params || {}, null, 2));
        
        try {
            if (!this.mcpClient) {
                throw new Error('MCP client not connected');
            }
            
            // Call the tool via MCP SDK
            const startTime = Date.now();
            const result = await this.mcpClient.callTool({
                name: command.tool,
                arguments: command.params || {}
            });
            const duration = Date.now() - startTime;
            
            console.log(`[Command Executor] Completed in ${duration}ms`);
            
            // Parse the result
            let parsedContent = result.content;
            if (Array.isArray(result.content) && result.content.length > 0) {
                parsedContent = result.content[0];
            }
            
            return {
                success: !result.isError,
                tool: command.tool,
                output: parsedContent?.text || parsedContent || 'Command executed successfully',
                duration: duration,
                timestamp: new Date().toISOString(),
                isError: result.isError || false
            };
            
        } catch (error) {
            console.error(`[Command Executor] Error:`, error.message || 'Unknown error');
            console.error(`[Command Executor] Error type:`, typeof error);
            console.error(`[Command Executor] Error constructor:`, error.constructor?.name);
            console.error(`[Command Executor] Full error:`, error);
            
            // Try to extract more details from the error
            let errorDetails = error.message || error.toString() || 'Unknown error occurred';
            
            // Add any additional error properties
            if (error.response) {
                errorDetails += `\nResponse: ${JSON.stringify(error.response)}`;
            }
            if (error.cause) {
                errorDetails += `\nCause: ${error.cause}`;
            }
            if (error.code) {
                errorDetails += `\nCode: ${error.code}`;
            }
            
            // Try to get error details from all properties
            const errorProps = Object.keys(error);
            if (errorProps.length > 0) {
                errorDetails += `\nError properties: ${errorProps.join(', ')}`;
                errorProps.forEach(prop => {
                    if (error[prop] && typeof error[prop] !== 'function') {
                        errorDetails += `\n${prop}: ${JSON.stringify(error[prop])}`;
                    }
                });
            }
            
            return {
                success: false,
                tool: command.tool,
                error: errorDetails,
                stack: error.stack || 'No stack trace',
                fullError: JSON.stringify(error, Object.getOwnPropertyNames(error)),
                errorType: error.constructor?.name || typeof error,
                timestamp: new Date().toISOString()
            };
        }
    }

    generateSummary(results) {
        const successful = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success).length;
        const totalDuration = results.reduce((sum, r) => sum + (r.duration || 0), 0);
        
        return {
            success: failed === 0,
            total_commands: results.length,
            successful,
            failed,
            total_duration_ms: totalDuration,
            average_duration_ms: results.length > 0 ? Math.round(totalDuration / results.length) : 0,
            results,
            timestamp: new Date().toISOString()
        };
    }
}

// CLI entry point
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.error('Usage: node mdc_executor.js <mdc-file-path> [--context <json>]');
        console.error('');
        console.error('Example:');
        console.error('  node mdc_executor.js automation.mdc');
        console.error('  node mdc_executor.js automation.mdc --context \'{"assetId": "123"}\'');
        process.exit(1);
    }
    
    const mdcFilePath = args[0];
    let context = {};
    
    // Parse context if provided
    const contextIndex = args.indexOf('--context');
    if (contextIndex !== -1 && args[contextIndex + 1]) {
        try {
            context = JSON.parse(args[contextIndex + 1]);
            console.log('[MDC Executor] Context:', JSON.stringify(context, null, 2));
        } catch (e) {
            console.error('Failed to parse context JSON:', e.message);
            process.exit(1);
        }
    }
    
    // Check if file exists
    if (!fs.existsSync(mdcFilePath)) {
        console.error(`MDC file not found: ${mdcFilePath}`);
        process.exit(1);
    }
    
    // Execute
    const executor = new MDCExecutor();
    const result = await executor.executeMDC(mdcFilePath, context);
    
    // Exit with appropriate code
    process.exit(result.success ? 0 : 1);
}

// ES module equivalent of checking if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

export { MDCExecutor };

