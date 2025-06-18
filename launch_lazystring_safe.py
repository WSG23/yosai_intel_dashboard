#!/usr/bin/env python3
"""
LazyString-Safe Debug Script
"""

# Load environment first
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

def main():
    """LazyString-safe app launcher"""
    print("🚀 Starting LazyString-Safe Yosai Intel Dashboard...")
    
    try:
        # Import app factory
        from core.app_factory import create_application
        
        app = create_application()
        if app:
            print("✅ App created successfully!")
            print("🔧 LazyString issues should be resolved")
            print("🌐 URL: http://127.0.0.1:8054")
            
            app.run(debug=True, host="127.0.0.1", port=8054)
        else:
            print("❌ Failed to create app")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
