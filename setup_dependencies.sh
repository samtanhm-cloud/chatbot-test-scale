#!/bin/bash
# Setup script to pre-install npm packages and Playwright browsers
# This can be run during build time to avoid timeouts

set -e

echo "🔧 Setting up dependencies for Streamlit MDC App..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if running on Streamlit Cloud
if [ "$STREAMLIT_RUNTIME_ENV" = "cloud" ] || [ -d "/mount/src" ]; then
    echo "☁️  Running on Streamlit Cloud"
    export DISPLAY=:99
    
    # Start Xvfb if not running
    if ! pgrep -x "Xvfb" > /dev/null; then
        echo "   Starting Xvfb virtual display..."
        Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
        sleep 2
    fi
fi

# Install npm packages
echo "📦 Installing npm packages..."
if [ -f "package.json" ]; then
    npm install --production --prefer-offline
    echo "✅ npm packages installed"
else
    echo "⚠️  No package.json found"
fi

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
if command -v npx &> /dev/null; then
    npx playwright install chromium
    
    # Create marker file
    touch .playwright_installed
    echo "✅ Playwright browsers installed"
else
    echo "⚠️  npx not found, skipping Playwright install"
fi

echo "✅ Setup complete!"

