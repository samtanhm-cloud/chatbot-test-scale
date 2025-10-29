#!/bin/bash

# Setup script for MDC Automation Executor
# This script sets up the environment for running the Streamlit app

set -e  # Exit on error

echo "🎭 MDC Automation Executor - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check Node.js version
echo "📌 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js $NODE_VERSION found"
echo ""

# Create virtual environment
echo "📦 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install
echo "✅ Node.js dependencies installed"
echo ""

# Install Playwright MCP Server
echo "🎭 Installing Playwright MCP Server..."
npx -y @executeautomation/playwright-mcp-server --help > /dev/null 2>&1 || true
echo "✅ Playwright MCP Server installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your Anthropic API key!"
    echo "   Open .env and replace 'your_api_key_here' with your actual API key"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p mdc_files
mkdir -p logs
mkdir -p results
echo "✅ Directories created"
echo ""

# Copy sample MDC file
if [ ! -f "mdc_files/sample_link_validator.mdc" ]; then
    echo "📄 Copying sample MDC file..."
    cp sample_link_validator.mdc mdc_files/
    echo "✅ Sample MDC file copied to mdc_files/"
    echo ""
fi

echo "=========================================="
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Anthropic API key"
echo "2. Add your MDC automation files to the mdc_files/ directory"
echo "3. Run the app with: streamlit run app.py"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "Happy automating! 🚀"

