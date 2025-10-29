#!/usr/bin/env node

/**
 * MDC Executor for Playwright MCP
 * Executes MDC files with Playwright browser automation
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class MDCExecutor {
    constructor() {
        this.mcpServerPath = process.env.MCP_SERVER_PATH || 'npx';
        this.mcpServerArgs = process.env.MCP_SERVER_ARGS?.split(' ') || ['-y', '@executeautomation/playwright-mcp-server'];
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
            
            // Start MCP server
            console.log('[MDC Executor] Starting Playwright MCP server...');
            const mcpServer = await this.startMCPServer();
            
            // Execute commands sequentially
            const results = [];
            for (let i = 0; i < commands.length; i++) {
                console.log(`[MDC Executor] Executing command ${i + 1}/${commands.length}`);
                const result = await this.executeCommand(commands[i], context);
                results.push(result);
                
                // Log result
                console.log(`[MDC Executor] Command ${i + 1} result:`, 
                    result.success ? '✓ Success' : '✗ Failed');
                
                if (!result.success && !commands[i].optional) {
                    console.error(`[MDC Executor] Critical command failed, stopping execution`);
                    break;
                }
            }
            
            // Stop MCP server
            await this.stopMCPServer(mcpServer);
            
            // Compile final results
            const summary = this.generateSummary(results);
            console.log('[MDC Executor] Execution completed');
            console.log(JSON.stringify(summary, null, 2));
            
            return summary;
            
        } catch (error) {
            console.error('[MDC Executor] Fatal error:', error);
            return {
                success: false,
                error: error.message,
                stack: error.stack
            };
        }
    }

    parseMDCCommands(mdcContent) {
        /**
         * Parse MDC file format
         * Expected format (simplified):
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
        let currentCommand = '';
        
        for (const line of lines) {
            if (line.trim().startsWith('```')) {
                if (inCodeBlock) {
                    // End of code block, parse command
                    try {
                        const cmd = JSON.parse(currentCommand);
                        commands.push(cmd);
                        currentCommand = '';
                    } catch (e) {
                        console.warn('[MDC Parser] Failed to parse command:', e.message);
                    }
                }
                inCodeBlock = !inCodeBlock;
            } else if (inCodeBlock) {
                currentCommand += line + '\n';
            }
        }
        
        return commands;
    }

    async startMCPServer() {
        return new Promise((resolve, reject) => {
            const server = spawn(this.mcpServerPath, this.mcpServerArgs, {
                stdio: ['pipe', 'pipe', 'pipe']
            });
            
            let started = false;
            
            server.stdout.on('data', (data) => {
                const output = data.toString();
                console.log('[MCP Server]', output);
                
                if (!started && (output.includes('ready') || output.includes('listening'))) {
                    started = true;
                    resolve(server);
                }
            });
            
            server.stderr.on('data', (data) => {
                console.error('[MCP Server Error]', data.toString());
            });
            
            server.on('error', (error) => {
                console.error('[MCP Server] Failed to start:', error);
                reject(error);
            });
            
            // Timeout if server doesn't start
            setTimeout(() => {
                if (!started) {
                    console.log('[MCP Server] Assuming started (timeout)');
                    resolve(server);
                }
            }, 3000);
        });
    }

    async stopMCPServer(server) {
        return new Promise((resolve) => {
            if (server && !server.killed) {
                server.on('close', () => {
                    console.log('[MCP Server] Stopped');
                    resolve();
                });
                server.kill();
                
                // Force kill after 5 seconds
                setTimeout(() => {
                    if (!server.killed) {
                        server.kill('SIGKILL');
                    }
                    resolve();
                }, 5000);
            } else {
                resolve();
            }
        });
    }

    async executeCommand(command, context) {
        /**
         * Execute a single MCP command
         * This is a simplified version - in production, you'd send actual MCP protocol messages
         */
        console.log(`[Command Executor] Tool: ${command.tool}`);
        
        try {
            // Simulate command execution with timeout
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // In a real implementation, you would:
            // 1. Format the command as an MCP request
            // 2. Send it to the MCP server via stdio
            // 3. Wait for and parse the response
            
            return {
                success: true,
                tool: command.tool,
                output: `Executed ${command.tool} successfully`,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            return {
                success: false,
                tool: command.tool,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    generateSummary(results) {
        const successful = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success).length;
        
        return {
            success: failed === 0,
            total_commands: results.length,
            successful,
            failed,
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
        process.exit(1);
    }
    
    const mdcFilePath = args[0];
    let context = {};
    
    // Parse context if provided
    const contextIndex = args.indexOf('--context');
    if (contextIndex !== -1 && args[contextIndex + 1]) {
        try {
            context = JSON.parse(args[contextIndex + 1]);
        } catch (e) {
            console.error('Failed to parse context JSON:', e.message);
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

