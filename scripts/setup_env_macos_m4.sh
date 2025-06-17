#!/bin/bash

echo "🔧 Setting up Yōsai Intel Dashboard environment on Apple Silicon..."

# 1. Ensure you're inside the project root
cd "$(dirname "$0")" || exit

# 2. Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# 4. Install geospatial dependencies
echo "🧱 Installing GEOS system library (required for shapely/geopandas)..."
brew install geos || echo "⚠️  Skipping GEOS install (already exists)"

export GEOS_CONFIG=/opt/homebrew/bin/geos-config
export CPLUS_INCLUDE_PATH=/opt/homebrew/include
export LIBRARY_PATH=/opt/homebrew/lib

# 5. Install Python packages (some built from source)
echo "📦 Installing required Python packages..."
pip install --no-binary shapely shapely
pip install --no-binary dash-leaflet dash-leaflet

# 6. Install remaining dependencies
pip install -r requirements.txt

# 7. Final note
echo "✅ Environment setup complete."
echo "📍 Activate anytime using: source venv/bin/activate"
