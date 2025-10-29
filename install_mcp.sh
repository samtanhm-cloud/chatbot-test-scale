#!/bin/bash

# Install script for MCP dependencies
# This ensures Node.js packages are installed before the app starts

echo "=== Installing MCP Dependencies ==="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js first."
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"

# Install npm packages
echo ""
echo "Installing npm packages..."
npm install

# Verify critical packages
echo ""
echo "Verifying installations..."

if npm list @modelcontextprotocol/sdk &> /dev/null; then
    echo "✓ @modelcontextprotocol/sdk installed"
else
    echo "❌ @modelcontextprotocol/sdk NOT installed"
    exit 1
fi

if npm list @executeautomation/playwright-mcp-server &> /dev/null; then
    echo "✓ @executeautomation/playwright-mcp-server installed"
else
    echo "❌ @executeautomation/playwright-mcp-server NOT installed"
    exit 1
fi

echo ""
echo "=== MCP Dependencies Installed Successfully! ==="
echo ""
echo "You can now run:"
echo "  node mdc_executor.js <mdc-file-path>"

