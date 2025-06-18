#!/bin/bash

# Install Dependencies Script
# This script ensures all required dependencies are installed

echo "🔍 Checking Python virtual environment..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "📋 It's recommended to use a virtual environment"
    echo ""
    echo "To create and activate one:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate  # On macOS/Linux"
    echo "# venv\\Scripts\\activate  # On Windows"
    echo ""
fi

echo "📦 Installing dependencies from requirements.txt..."

# Upgrade pip first
python3 -m pip install --upgrade pip

# Install all requirements
python3 -m pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"

# Verify flask-login installation
echo "🔍 Verifying flask-login installation..."
python3 -c "import flask_login; print(f'✅ flask-login {flask_login.__version__} installed successfully')" 2>/dev/null || echo "❌ flask-login installation failed"

echo "🚀 Ready to run: python3 app.py"
