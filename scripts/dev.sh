#!/bin/bash
# Development helper script

set -e

echo "🚀 Yōsai Intel Dashboard - Development Setup"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python test_modular_system.py

# Start application
echo "🎯 Starting application..."
python app.py
