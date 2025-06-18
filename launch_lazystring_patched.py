#!/usr/bin/env python3
"""
LazyString-Patched App Startup
Applies aggressive LazyString fixes before any imports
"""

# Apply LazyString fix FIRST, before any other imports
print("🔧 Applying LazyString patches...")

import json
import sys

# Monkey patch JSON globally BEFORE importing Dash
original_default = json.JSONEncoder.default

def global_lazystring_handler(self, obj):
    """Global handler for LazyString and other non-serializable objects"""
    # Handle LazyString objects from Flask-Babel
    if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
        return str(obj)
    
    # Handle Babel lazy objects
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        try:
            return str(obj)
        except:
            return f"LazyString({obj.__class__.__name__})"
    
    # Handle functions
    if callable(obj):
        return f"Function: {getattr(obj, '__name__', 'anonymous')}"
    
    # Handle other non-serializable objects
    try:
        return original_default(self, obj)
    except TypeError:
        return str(obj)

# Apply the patch
json.JSONEncoder.default = global_lazystring_handler
print("✅ Global LazyString JSON patch applied")

# Now load environment
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    if Path(".env").exists():
        load_dotenv(override=True)
        print("✅ Loaded .env file")
except ImportError:
    pass

# Set required variables
required_vars = {
    "DB_HOST": "localhost",
    "SECRET_KEY": "dev-secret-12345",
    "AUTH0_CLIENT_ID": "dev-client-id",
    "AUTH0_CLIENT_SECRET": "dev-client-secret", 
    "AUTH0_DOMAIN": "dev.auth0.com",
    "AUTH0_AUDIENCE": "dev-audience",
    "YOSAI_ENV": "development"
}

for var, default in required_vars.items():
    if not os.getenv(var):
        os.environ[var] = default

# NOW import your app (after patches are applied)
if __name__ == "__main__":
    print("🚀 Starting LazyString-Patched Yosai Intel Dashboard...")
    
    try:
        from core.app_factory import create_application
        
        app = create_application()
        if app:
            print("✅ App created with LazyString patches")
            print("🌐 URL: http://127.0.0.1:8056")
            print("🔧 LazyString errors should be completely eliminated")
            
            app.run(debug=True, host="127.0.0.1", port=8056)
        else:
            print("❌ Failed to create app")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
