#!/bin/bash
# Quick setup script for job automation system

echo "=================================="
echo "Job Automation System Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p browser_data

# Copy environment template
echo ""
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file"
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Edit resume_data.json with your information"
echo "3. Edit config.yaml to customize settings"
echo "4. Run: python main.py run-all --limit 5 --dry-run"
echo ""
echo "For help: python main.py --help"
echo ""
