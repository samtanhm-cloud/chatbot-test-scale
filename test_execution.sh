#!/bin/bash
# Quick test script to verify MDC execution

echo "🔍 Testing Node.js MDC Execution"
echo "=================================="
echo ""

cd "/Users/tansa/Desktop/Playwright mcp rule file/streamlit_mdc_app"

echo "1. Checking Node.js..."
which node
node --version
echo ""

echo "2. Checking mdc_executor.js..."
ls -lh mdc_executor.js
echo ""

echo "3. Checking MDC file..."
ls -lh mdc_files/test-browser-simple.mdc
echo ""

echo "4. Running MDC execution..."
echo "=================================="
node mdc_executor.js mdc_files/test-browser-simple.mdc
EXITCODE=$?
echo "=================================="
echo "Exit code: $EXITCODE"

