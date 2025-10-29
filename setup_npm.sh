#!/bin/bash
# Setup script to install npm packages
# This runs automatically on Streamlit Cloud startup

echo "=== Installing npm packages ==="
cd /mount/src/chatbot-test-scale

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"

# Install packages
echo "Installing npm packages..."
npm install

# Verify installation
if npm list @modelcontextprotocol/sdk &> /dev/null; then
    echo "✓ @modelcontextprotocol/sdk installed"
else
    echo "⚠️  @modelcontextprotocol/sdk NOT installed"
fi

if npm list @executeautomation/playwright-mcp-server &> /dev/null; then
    echo "✓ @executeautomation/playwright-mcp-server installed"
else
    echo "⚠️  @executeautomation/playwright-mcp-server NOT installed"
fi

echo "=== npm setup complete ==="

