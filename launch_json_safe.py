#!/usr/bin/env python3
"""
Fixed App Launcher - Uses JSON-safe components
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
    print("⚠️  python-dotenv not available")

# Set required variables
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("SECRET_KEY", "dev-secret-12345")
os.environ.setdefault("YOSAI_ENV", "development")

if __name__ == "__main__":
    print("🚀 Starting JSON-Safe Yosai Intel Dashboard...")
    
    try:
        # Use the JSON-safe app factory
        from core.app_factory_json_safe import create_application
        
        app = create_application()
        if app:
            print("✅ JSON-safe app created successfully")
            print("🌐 URL: http://127.0.0.1:8050")
            print("🔧 All JSON serialization issues resolved")
            
            app.run_server(debug=True, host="127.0.0.1", port=8050)
        else:
            print("❌ Failed to create app")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🎯 Try the minimal app instead: python3 minimal_working_app.py")
