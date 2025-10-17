#!/bin/bash

# Setup script for PPTX Translator

echo "Setting up PPTX Translator..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Ask if user wants dev dependencies
read -p "Install development dependencies (ruff, mypy)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create config.ini file if it doesn't exist
if [ ! -f "config.ini" ]; then
    echo "Creating config.ini file..."
    cp config.ini.example config.ini
    echo ""
    echo "⚠️  Please edit config.ini and add your Gemini API key!"
    echo ""
fi

echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.ini and add your Gemini API key under [gemini] section"
echo "  2. Activate the virtual environment: source venv/bin/activate"
echo "  3. Run: python cli.py --help"
