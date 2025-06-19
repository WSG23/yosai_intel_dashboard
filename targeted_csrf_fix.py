#!/usr/bin/env python3
"""
Targeted CSRF Fix for Yosai Dashboard
Patches the exact CSRFProtect call in your app_factory.py

Your app_factory.py has: CSRFProtect(server)
This always enables CSRF regardless of environment variables.
This script patches CSRFProtect to be a no-op when CSRF is disabled.
"""

import os
import sys

def patch_csrf_protect():
    """Patch CSRFProtect before any imports"""
    print("🛡️ Patching CSRFProtect...")
    
    # Set environment first
    os.environ.update({
        'WTF_CSRF_ENABLED': 'False',
        'CSRF_ENABLED': 'False',
        'SECRET_KEY': 'dev-secret-key-12345',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1',
        'YOSAI_ENV': 'development',
        'DB_HOST': 'localhost',
        'AUTH0_CLIENT_ID': 'dev-client-id-12345',
        'AUTH0_CLIENT_SECRET': 'dev-client-secret-12345',
        'AUTH0_DOMAIN': 'dev-domain.auth0.com'
    })
    
    # Patch flask_wtf.csrf.CSRFProtect
    try:
        import flask_wtf.csrf
        
        original_csrf_protect = flask_wtf.csrf.CSRFProtect
        
        class NoOpCSRFProtect:
            """No-operation CSRFProtect that does nothing when CSRF is disabled"""
            
            def __init__(self, app=None):
                # Check if CSRF should be enabled
                csrf_enabled = os.getenv('WTF_CSRF_ENABLED', 'True').lower() == 'true'
                
                if csrf_enabled:
                    # Use real CSRFProtect
                    self._real_csrf = original_csrf_protect(app)
                    self._enabled = True
                    print("   ✅ CSRF enabled (real CSRFProtect)")
                else:
                    # No-op mode
                    self._real_csrf = None
                    self._enabled = False
                    print("   ✅ CSRF disabled (no-op CSRFProtect)")
                    
                    # If app provided, disable CSRF in config
                    if app:
                        app.config.update({
                            'WTF_CSRF_ENABLED': False,
                            'WTF_CSRF_CHECK_DEFAULT': False,
                            'CSRF_ENABLED': False
                        })
            
            def init_app(self, app):
                if self._enabled and self._real_csrf:
                    return self._real_csrf.init_app(app)
                else:
                    # Disable CSRF in app config
                    app.config.update({
                        'WTF_CSRF_ENABLED': False,
                        'WTF_CSRF_CHECK_DEFAULT': False,
                        'CSRF_ENABLED': False
                    })
                    print("   ✅ CSRF disabled in Flask app config")
            
            def protect(self):
                if self._enabled and self._real_csrf:
                    return self._real_csrf.protect()
                else:
                    # Return identity function (no protection)
                    return lambda f: f
            
            def exempt(self, view):
                if self._enabled and self._real_csrf:
                    return self._real_csrf.exempt(view)
                else:
                    # No-op for exempt
                    return view
            
            def __getattr__(self, name):
                # Delegate to real CSRF if enabled
                if self._enabled and self._real_csrf:
                    return getattr(self._real_csrf, name)
                else:
                    # Return no-op function for any other method
                    return lambda *args, **kwargs: None
        
        # Replace CSRFProtect with our conditional version
        flask_wtf.csrf.CSRFProtect = NoOpCSRFProtect
        
        # Also patch the direct import path
        import flask_wtf
        flask_wtf.CSRFProtect = NoOpCSRFProtect
        
        print("   ✅ CSRFProtect patched successfully")
        return True
        
    except ImportError:
        print("   ⚠️ flask-wtf not available")
        return False
    except Exception as e:
        print(f"   ❌ CSRFProtect patch failed: {e}")
        return False

def apply_lazystring_fix():
    """Apply LazyString fix"""
    print("🛠️ Applying LazyString fix...")
    
    import json
    original_default = json.JSONEncoder.default
    
    def safe_json_handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            return str(obj)
        try:
            return original_default(self, obj)
        except (TypeError, AttributeError):
            return str(obj)
    
    json.JSONEncoder.default = safe_json_handler
    print("   ✅ LazyString fix applied")

def main():
    """Main function"""
    print("🎯 Targeted CSRF Fix for Yosai Dashboard")
    print("=" * 45)
    print("Patching CSRFProtect before app creation...\n")
    
    try:
        # Step 1: Patch CSRFProtect BEFORE any app imports
        patch_csrf_protect()
        
        # Step 2: Apply LazyString fix
        apply_lazystring_fix()
        
        # Step 3: Load .env if available
        try:
            from dotenv import load_dotenv
            from pathlib import Path
            if Path('.env').exists():
                load_dotenv()
                # Ensure CSRF stays disabled
                os.environ['WTF_CSRF_ENABLED'] = 'False'
                print("✅ Loaded .env with CSRF override")
        except ImportError:
            pass
        
        # Step 4: Import and create app (after patches)
        print("\n🚀 Creating app with patched CSRFProtect...")
        from core.app_factory import create_application
        
        app = create_application()
        
        if app is None:
            print("❌ App creation failed")
            return 1
        
        print(f"✅ App created successfully: {type(app).__name__}")
        
        # Step 5: Final check - ensure CSRF is disabled
        if hasattr(app, 'server'):
            app.server.config.update({
                'WTF_CSRF_ENABLED': False,
                'WTF_CSRF_CHECK_DEFAULT': False,
                'CSRF_ENABLED': False
            })
            print("✅ Final CSRF disable applied")
        
        # Step 6: Start the app
        print("\n🌐 Starting server at http://127.0.0.1:8050")
        print("🛡️ CSRF protection bypassed via patch")
        print("🔧 LazyString fixes applied")
        print("🛑 Press Ctrl+C to stop\n")
        
        app.run(debug=True, host='127.0.0.1', port=8050)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())