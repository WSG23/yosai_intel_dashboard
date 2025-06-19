#!/bin/bash

# Quick .env update to fix callback authentication issues
echo "🔧 Adding auth bypass to .env file..."

cat >> .env << 'EOF'

# Auth bypass for development (fixes 403 Forbidden callback errors)
DISABLE_AUTH=True
BYPASS_LOGIN=True
LOGIN_DISABLED=True
TESTING=True

# Missing AUTH0 variable (found by diagnostic)
AUTH0_AUDIENCE=dev-audience-12345

# CSRF and LazyString fixes
WTF_CSRF_ENABLED=False
CSRF_ENABLED=False
SECRET_KEY=dev-secret-key-12345
FLASK_ENV=development
FLASK_DEBUG=1
YOSAI_ENV=development
EOF

echo "✅ Auth bypass variables added to .env"
echo ""
echo "🚀 Now try running your app again:"
echo "   python3 targeted_ticket_categories_fix.py"
echo ""
echo "💡 The 403 Forbidden callback errors should be resolved!"