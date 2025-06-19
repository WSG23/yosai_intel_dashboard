#!/usr/bin/env python3
"""
Simple Working Launcher for Yosai Dashboard
Avoids all the problematic hasattr checks that cause ObsoleteAttributeException

This launcher:
1. Sets up environment
2. Applies LazyString fixes 
3. Creates app
4. Runs app with app.run() (avoiding run_server completely)
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup basic environment"""
    print("🔧 Setting up environment...")
    
    # Set essential environment variables
    env_vars = {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1',
        'SECRET_KEY': 'dev-secret-key-12345',
        'YOSAI_ENV': 'development',
        'WTF_CSRF_ENABLED': 'False',
        'DB_HOST': 'localhost',
        'AUTH0_CLIENT_ID': 'dev-client-id-12345',
        'AUTH0_CLIENT_SECRET': 'dev-client-secret-12345',
        'AUTH0_DOMAIN': 'dev-domain.auth0.com'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    # Load .env if available
    try:
        from dotenv import load_dotenv
        if Path('.env').exists():
            load_dotenv(override=True)
            print("   ✅ Loaded .env file")
    except ImportError:
        print("   ⚠️ python-dotenv not available")

def apply_lazystring_fixes():
    """Apply LazyString fixes"""
    print("🛠️ Applying LazyString fixes...")
    
    try:
        from lazystring_plugin import apply_lazystring_fixes
        success = apply_lazystring_fixes(debug_mode=True)
        if success:
            print("   ✅ LazyString protection activated")
            return True
        else:
            print("   ❌ LazyString protection failed")
            return False
    except ImportError:
        print("   ⚠️ LazyString plugin not found, applying basic fixes...")
        # Basic fallback JSON fix
        import json
        original_default = json.JSONEncoder.default
        
        def safe_json_handler(self, obj):
            if 'LazyString' in str(type(obj)):
                return str(obj)
            if hasattr(obj, '_func') and hasattr(obj, '_args'):
                return str(obj)
            try:
                return original_default(self, obj)
            except TypeError:
                return str(obj)
        
        json.JSONEncoder.default = safe_json_handler
        print("   ✅ Basic LazyString fix applied")
        return True

def create_and_run_app():
    """Create and run the app"""
    print("🚀 Creating and starting app...")
    
    try:
        # Import app factory
        from core.app_factory import create_application
        
        # Create app
        app = create_application()
        
        if app is None:
            print("   ❌ App creation failed - app factory returned None")
            return 1
        
        print(f"   ✅ App created successfully: {type(app).__name__}")
        
        # Run the app - NO hasattr checks, just use app.run directly
        print("   🌐 Starting server at http://127.0.0.1:8050")
        print("   🔧 LazyString errors should be eliminated")
        print("   🛑 Press Ctrl+C to stop\n")
        
        # Your app uses Flask's run method (not run_server)
        app.run(debug=True, host='127.0.0.1', port=8050)
        
        return 0
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1

def main():
    """Main launcher function"""
    print("🎯 Simple Yosai Dashboard Launcher")
    print("=" * 40)
    
    try:
        # Setup environment
        setup_environment()
        
        # Apply LazyString fixes
        apply_lazystring_fixes()
        
        # Create and run app
        return create_and_run_app()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())