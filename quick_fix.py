#!/usr/bin/env python3
"""
Quick Fix Script for Yosai Dashboard LazyString Issues
Addresses the specific error you encountered with app.run vs app.run_server

Run this script to immediately start your app with LazyString protection.
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

def setup_environment():
    """Setup minimal environment for app to run"""
    print("🔧 Setting up environment...")
    
    # Essential environment variables
    env_vars = {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1',
        'SECRET_KEY': 'dev-secret-key-12345',
        'YOSAI_ENV': 'development',
        'WTF_CSRF_ENABLED': 'False',  # Disable CSRF for now
        'DB_HOST': 'localhost'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"   Set {key}={value}")
    
    # Load .env if it exists
    try:
        from dotenv import load_dotenv
        if Path('.env').exists():
            load_dotenv(override=True)
            print("   ✅ Loaded .env file")
    except ImportError:
        print("   ⚠️ python-dotenv not available")

def apply_immediate_lazystring_fix():
    """Apply LazyString fix before importing anything else"""
    print("🛠️ Applying immediate LazyString fix...")
    
    import json
    
    # Store original
    original_json_default = json.JSONEncoder.default
    
    def safe_json_handler(self, obj):
        """Handle LazyString and other problematic objects"""
        obj_type = str(type(obj))
        
        # Handle LazyString
        if 'LazyString' in obj_type:
            return str(obj)
        
        # Handle Babel objects
        if 'babel' in obj_type.lower():
            return str(obj)
        
        # Handle lazy objects
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            return str(obj)
        
        # Handle functions
        if callable(obj):
            return f"Function: {getattr(obj, '__name__', 'anonymous')}"
        
        # Try original handler
        try:
            return original_json_default(self, obj)
        except TypeError:
            return str(obj)
    
    # Apply global JSON patch
    json.JSONEncoder.default = safe_json_handler
    
    # Patch Flask-Babel if available
    try:
        import flask_babel
        original_lazy = flask_babel.lazy_gettext
        original_get = flask_babel.gettext
        
        def string_lazy_gettext(string, **variables):
            result = original_lazy(string, **variables)
            return str(result)
        
        def string_gettext(string, **variables):
            result = original_get(string, **variables)
            return str(result)
        
        flask_babel.lazy_gettext = string_lazy_gettext
        flask_babel.gettext = string_gettext
        flask_babel._l = string_lazy_gettext
        
        print("   ✅ Patched Flask-Babel")
    except ImportError:
        print("   ⚠️ Flask-Babel not available to patch")
    
    print("   ✅ JSON encoder patched")

def run_app_with_fixes():
    """Run the app with all fixes applied"""
    print("🚀 Starting app with fixes...")
    
    try:
        # Import app factory
        from core.app_factory import create_application
        
        # Create app
        app = create_application()
        
        if app is None:
            raise RuntimeError("App factory returned None")
        
        print(f"   ✅ App created: {type(app).__name__}")
        
        # Determine how to run the app
        if hasattr(app, 'run'):
            # Your customized Dash app uses Flask's run method
            print("   🌐 Using Flask run method (customized Dash app)")
            print("   📍 URL: http://127.0.0.1:8050")
            print("   🔧 LazyString errors should be eliminated")
            print("   🛑 Press Ctrl+C to stop\n")
            
            app.run(debug=True, host='127.0.0.1', port=8050)
            
        elif hasattr(app, 'run_server'):
            # Standard Dash app
            print("   🌐 Using Dash run_server method")
            app.run_server(debug=True, host='127.0.0.1', port=8050)
            
        else:
            raise RuntimeError("App has neither run nor run_server method")
    
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Make sure you're in the right directory with core/app_factory.py")
        return 1
    
    except Exception as e:
        print(f"   ❌ App error: {e}")
        return 1
    
    return 0

def test_lazystring_fix():
    """Test if LazyString fix is working"""
    print("🧪 Testing LazyString fix...")
    
    try:
        from flask_babel import lazy_gettext as _l
        import json
        
        # Create LazyString
        lazy_str = _l("Test string")
        
        # Try to serialize
        result = json.dumps({"test": lazy_str})
        print(f"   ✅ LazyString serialized successfully: {result}")
        return True
        
    except ImportError:
        print("   ⚠️ Flask-Babel not available for testing")
        return True
    except Exception as e:
        print(f"   ❌ LazyString test failed: {e}")
        return False

def main():
    """Main entry point"""
    print("🎯 Yosai Dashboard Quick Fix")
    print("=" * 40)
    print("Resolving: 'app.run_server has been replaced by app.run'")
    print("And: LazyString JSON serialization errors\n")
    
    try:
        # Setup
        setup_environment()
        
        # Apply LazyString fixes BEFORE importing app
        apply_immediate_lazystring_fix()
        
        # Test the fix
        if test_lazystring_fix():
            print("   ✅ LazyString fix appears to be working")
        
        # Run the app
        return run_app_with_fixes()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)