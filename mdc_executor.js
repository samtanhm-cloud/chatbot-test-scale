#!/usr/bin/env node

/**
 * MDC Executor for Playwright MCP - REAL IMPLEMENTATION
 * Executes MDC files with actual Playwright browser automation via MCP SDK
 * Version: 2.0.0 - Production Ready
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

class MDCExecutor {
    constructor() {
        this.mcpServerPath = process.env.MCP_SERVER_PATH || 'npx';
        this.mcpServerArgs = process.env.MCP_SERVER_ARGS?.split(' ') || 
            ['-y', '@executeautomation/playwright-mcp-server'];
        this.mcpClient = null;
        this.mcpServerProcess = null;
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
                    console.error(`[MDC Executor] Error:`, result.error);
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
        return new Promise(async (resolve, reject) => {
            try {
                // Spawn the MCP server process
                console.log(`[MCP Server] Starting: ${this.mcpServerPath} ${this.mcpServerArgs.join(' ')}`);
                this.mcpServerProcess = spawn(this.mcpServerPath, this.mcpServerArgs, {
                    stdio: ['pipe', 'pipe', 'pipe']
                });
                
                // Handle process errors
                this.mcpServerProcess.on('error', (error) => {
                    console.error('[MCP Server] Process error:', error);
                    reject(error);
                });
                
                // Log stderr
                this.mcpServerProcess.stderr.on('data', (data) => {
                    const message = data.toString().trim();
                    if (message) {
                        console.error('[MCP Server stderr]', message);
                    }
                });
                
                // Create MCP client with stdio transport
                const transport = new StdioClientTransport({
                    stdin: this.mcpServerProcess.stdin,
                    stdout: this.mcpServerProcess.stdout
                });
                
                this.mcpClient = new Client({
                    name: 'mdc-executor',
                    version: '2.0.0'
                }, {
                    capabilities: {
                        tools: {}
                    }
                });
                
                // Connect the client
                await this.mcpClient.connect(transport);
                console.log('[MCP Server] Connected successfully');
                
                // List available tools
                const toolsList = await this.mcpClient.listTools();
                console.log(`[MCP Server] Available tools: ${toolsList.tools.length}`);
                toolsList.tools.forEach(tool => {
                    console.log(`[MCP Server]   - ${tool.name}`);
                });
                
                resolve();
                
            } catch (error) {
                console.error('[MCP Server] Failed to start:', error);
                reject(error);
            }
        });
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
            
            // Kill server process
            if (this.mcpServerProcess && !this.mcpServerProcess.killed) {
                this.mcpServerProcess.kill();
                
                // Wait for process to exit
                await new Promise((resolve) => {
                    const timeout = setTimeout(() => {
                        if (!this.mcpServerProcess.killed) {
                            this.mcpServerProcess.kill('SIGKILL');
                        }
                        resolve();
                    }, 5000);
                    
                    this.mcpServerProcess.on('close', () => {
                        clearTimeout(timeout);
                        resolve();
                    });
                });
                
                this.mcpServerProcess = null;
                console.log('[MCP Server] Process stopped');
            }
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
            console.error(`[Command Executor] Error:`, error.message);
            
            return {
                success: false,
                tool: command.tool,
                error: error.message,
                stack: error.stack,
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

if (require.main === module) {
    main().catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

module.exports = { MDCExecutor };

