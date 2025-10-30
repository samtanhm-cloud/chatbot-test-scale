#!/usr/bin/env node

/**
 * Simple script to list all available MCP tools
 * This helps debug what tools the Playwright MCP server actually provides
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

async function listTools() {
    console.log('='.repeat(60));
    console.log('MCP TOOL LISTER');
    console.log('='.repeat(60));
    console.log('');
    
    try {
        // Create MCP client
        console.log('Creating MCP client...');
        const mcpClient = new Client({
            name: 'tool-lister',
            version: '1.0.0'
        }, {
            capabilities: {
                tools: {}
            }
        });

        // Configure environment for headless mode
        const env = {
            ...process.env,
            PLAYWRIGHT_HEADLESS: '1',
            PLAYWRIGHT_BROWSERS_PATH: '0',
            HEADLESS: 'true'
        };

        // Start the MCP server
        console.log('Starting Playwright MCP server...');
        console.log('Command: npx -y @executeautomation/playwright-mcp-server');
        console.log('');
        
        const transport = new StdioClientTransport({
            command: 'npx',
            args: ['-y', '@executeautomation/playwright-mcp-server'],
            env: env
        });

        // Connect
        console.log('Connecting to MCP server...');
        await mcpClient.connect(transport);
        console.log('✅ Connected successfully!');
        console.log('');

        // List tools
        console.log('Fetching tools list...');
        const toolsList = await mcpClient.listTools();
        
        console.log('='.repeat(60));
        console.log(`FOUND ${toolsList.tools.length} TOOLS:`);
        console.log('='.repeat(60));
        console.log('');

        if (toolsList.tools && toolsList.tools.length > 0) {
            toolsList.tools.forEach((tool, index) => {
                console.log(`${index + 1}. ${tool.name}`);
                if (tool.description) {
                    // Wrap description
                    const desc = tool.description.split('\n')[0]; // First line only
                    console.log(`   ${desc.substring(0, 100)}${desc.length > 100 ? '...' : ''}`);
                }
                console.log('');
            });
        } else {
            console.log('⚠️  NO TOOLS FOUND!');
        }

        console.log('='.repeat(60));
        console.log('DONE');
        console.log('='.repeat(60));

        // Close connection
        await mcpClient.close();
        process.exit(0);

    } catch (error) {
        console.error('');
        console.error('❌ ERROR:', error.message);
        console.error('');
        console.error('Stack:', error.stack);
        process.exit(1);
    }
}

// Run it
listTools();

