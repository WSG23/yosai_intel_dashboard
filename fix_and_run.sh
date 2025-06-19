#!/bin/bash

# One Command Fix for Yosai Dashboard
# Fixes all remaining issues and starts the app

echo "🎯 One Command Fix for Yosai Dashboard"
echo "======================================"

# Step 1: Install flask-babel
echo "📦 Installing flask-babel..."
pip install flask-babel

# Step 2: Set environment variables
echo "🔧 Setting environment variables..."
export FLASK_ENV=development
export FLASK_DEBUG=1
export SECRET_KEY=dev-secret-key-12345
export YOSAI_ENV=development
export WTF_CSRF_ENABLED=False
export DB_HOST=localhost
export AUTH0_CLIENT_ID=dev-client-id-12345
export AUTH0_CLIENT_SECRET=dev-client-secret-12345
export AUTH0_DOMAIN=dev-domain.auth0.com

# Step 3: Add to .env file for persistence
echo "📝 Adding to .env file..."
cat >> .env << 'EOF'

# Fixed environment variables
AUTH0_CLIENT_ID=dev-client-id-12345
AUTH0_CLIENT_SECRET=dev-client-secret-12345
AUTH0_DOMAIN=dev-domain.auth0.com
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-12345
YOSAI_ENV=development
WTF_CSRF_ENABLED=False
DB_HOST=localhost
EOF

echo "✅ Setup complete!"
echo ""
echo "🚀 Now run:"
echo "   python3 simple_launcher.py"
echo ""
echo "📍 App will be available at: http://127.0.0.1:8050"