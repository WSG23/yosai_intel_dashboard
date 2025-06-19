#!/usr/bin/env python3
"""
Role Required Decorator Fix
Patches the @role_required decorator to bypass authentication in development

The issue: @role_required("admin") returns ["Forbidden", 403] (2 values)
But your callback expects 3 values.

This script patches the role_required decorator to bypass auth in development.
"""

import os
import sys
import json
from pathlib import Path

def setup_environment():
    """Setup environment with auth bypass"""
    print("🔧 Setting up environment with auth bypass...")
    
    env_vars = {
        'WTF_CSRF_ENABLED': 'False',
        'CSRF_ENABLED': 'False',
        'SECRET_KEY': 'dev-secret-key-12345',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1',
        'YOSAI_ENV': 'development',
        'DB_HOST': 'localhost',
        'AUTH0_CLIENT_ID': 'dev-client-id-12345',
        'AUTH0_CLIENT_SECRET': 'dev-client-secret-12345',
        'AUTH0_DOMAIN': 'dev-domain.auth0.com',
        'AUTH0_AUDIENCE': 'dev-audience-12345',
        'DISABLE_AUTH': 'True',
        'BYPASS_LOGIN': 'True',
        'LOGIN_DISABLED': 'True',
        'TESTING': 'True'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # Load .env with overrides
    try:
        from dotenv import load_dotenv
        if Path('.env').exists():
            load_dotenv()
            # Ensure critical overrides
            for key in ['DISABLE_AUTH', 'BYPASS_LOGIN', 'LOGIN_DISABLED']:
                if key in env_vars:
                    os.environ[key] = env_vars[key]
    except ImportError:
        pass
    
    print("   ✅ Environment set with strong auth bypass")

def apply_basic_patches():
    """Apply basic JSON and CSRF patches"""
    print("🔧 Applying basic patches...")
    
    # JSON patch for LazyString
    original_default = json.JSONEncoder.default
    def safe_json_handler(self, obj):
        if 'LazyString' in str(type(obj)) or 'speaklater' in str(type(obj)):
            return str(obj)
        try:
            return original_default(self, obj)
        except (TypeError, AttributeError):
            return str(obj)
    json.JSONEncoder.default = safe_json_handler
    
    # Flask-Babel patch
    try:
        import flask_babel
        original_lazy = flask_babel.lazy_gettext
        flask_babel.lazy_gettext = lambda s, **k: str(original_lazy(s, **k))
        flask_babel._l = flask_babel.lazy_gettext
    except ImportError:
        pass
    
    # CSRF patch
    try:
        import flask_wtf.csrf
        class NoOpCSRF:
            def __init__(self, app=None):
                if app: app.config['WTF_CSRF_ENABLED'] = False
            def init_app(self, app): 
                app.config['WTF_CSRF_ENABLED'] = False
            def protect(self): 
                return lambda f: f
            def exempt(self, view): 
                return view
            def __getattr__(self, name): 
                return lambda *a, **k: None
        
        flask_wtf.csrf.CSRFProtect = NoOpCSRF
    except ImportError:
        pass
    
    # Fix TICKET_CATEGORIES
    try:
        import components.incident_alerts_panel as panel
        if hasattr(panel, 'TICKET_CATEGORIES'):
            original = panel.TICKET_CATEGORIES
            if isinstance(original, dict):
                panel.TICKET_CATEGORIES = {str(k): str(v) for k, v in original.items()}
            else:
                panel.TICKET_CATEGORIES = str(original)
    except:
        pass
    
    print("   ✅ Basic patches applied")

def patch_role_required_decorator():
    """Patch the @role_required decorator to bypass auth in development"""
    print("🎯 Patching @role_required decorator...")
    
    try:
        import core.auth as auth_module
        
        # Check if we should bypass auth
        should_bypass = (
            os.getenv('DISABLE_AUTH', 'False').lower() == 'true' or
            os.getenv('BYPASS_LOGIN', 'False').lower() == 'true' or
            os.getenv('LOGIN_DISABLED', 'False').lower() == 'true' or
            os.getenv('FLASK_ENV', '') == 'development'
        )
        
        if should_bypass:
            # Store original decorator
            original_role_required = auth_module.role_required
            
            def bypassed_role_required(role: str):
                """Bypassed role_required that does nothing in development"""
                def decorator(func):
                    print(f"   🔓 Bypassing role_required('{role}') for {func.__name__}")
                    return func  # Return function unchanged - no auth check!
                return decorator
            
            # Replace the decorator
            auth_module.role_required = bypassed_role_required
            
            print(f"   ✅ @role_required decorator bypassed (DISABLE_AUTH={should_bypass})")
        else:
            print("   ⚠️ Auth bypass not enabled in environment")
        
        return True
        
    except ImportError:
        print("   ❌ Could not import core.auth module")
        return False
    except Exception as e:
        print(f"   ❌ Error patching role_required: {e}")
        return False

def patch_login_required_decorator():
    """Also patch @login_required if it exists"""
    print("🔓 Patching @login_required decorator...")
    
    try:
        import core.auth as auth_module
        
        should_bypass = (
            os.getenv('DISABLE_AUTH', 'False').lower() == 'true' or
            os.getenv('LOGIN_DISABLED', 'False').lower() == 'true'
        )
        
        if should_bypass and hasattr(auth_module, 'login_required'):
            # Store original
            original_login_required = auth_module.login_required
            
            def bypassed_login_required(func):
                """Bypassed login_required that does nothing"""
                print(f"   🔓 Bypassing login_required for {func.__name__}")
                return func  # Return function unchanged
            
            # Replace the decorator  
            auth_module.login_required = bypassed_login_required
            
            print("   ✅ @login_required decorator bypassed")
        
        # Also try to patch flask_login if imported
        try:
            import flask_login
            if should_bypass:
                def bypass_flask_login(func):
                    return func
                flask_login.login_required = bypass_flask_login
                print("   ✅ flask_login.login_required bypassed")
        except ImportError:
            pass
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ login_required patch failed: {e}")
        return False

def test_auth_patches():
    """Test that auth patches are working"""
    print("🧪 Testing auth patches...")
    
    try:
        from core.auth import role_required
        
        # Test the decorator
        @role_required("admin")
        def test_function():
            return "success"
        
        # This should work without authentication now
        result = test_function()
        if result == "success":
            print("   ✅ @role_required decorator bypass working")
            return True
        else:
            print(f"   ❌ @role_required still blocking: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Auth patch test failed: {e}")
        return False

def main():
    """Main function to fix the role_required issue"""
    print("🎯 Role Required Decorator Fix")
    print("=" * 35)
    print("Fixing @role_required('admin') callback authentication...\n")
    
    try:
        # Step 1: Setup environment
        setup_environment()
        
        # Step 2: Apply basic patches
        apply_basic_patches()
        
        # Step 3: Patch role_required decorator BEFORE importing app
        role_patch_success = patch_role_required_decorator()
        
        # Step 4: Patch login_required decorator
        login_patch_success = patch_login_required_decorator()
        
        # Step 5: Test patches
        if role_patch_success:
            test_auth_patches()
        
        # Step 6: Import and create app (after patches)
        print("\n🚀 Creating app with auth decorators bypassed...")
        from core.app_factory import create_application
        
        app = create_application()
        
        if app is None:
            print("❌ App creation failed")
            return 1
        
        print(f"✅ App created successfully: {type(app).__name__}")
        
        # Step 7: Configure app for development
        if hasattr(app, 'server'):
            app.server.config.update({
                'WTF_CSRF_ENABLED': False,
                'CSRF_ENABLED': False,
                'LOGIN_DISABLED': True,
                'TESTING': True,
                'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret')
            })
            print("   ✅ App configured for development")
        
        # Step 8: Check callbacks
        if hasattr(app, 'callback_map') and app.callback_map:
            callback_count = len(app.callback_map)
            print(f"   📊 Found {callback_count} callbacks")
            
            # Look for the problematic callback
            for callback_id, callback in app.callback_map.items():
                if hasattr(callback, 'output') and callback.output:
                    outputs = callback.output if isinstance(callback.output, list) else [callback.output]
                    output_ids = [str(output.component_id) for output in outputs]
                    if 'upload-status' in output_ids:
                        print(f"   🎯 Found upload callback: {len(outputs)} outputs expected")
        
        # Step 9: Start the app
        print("\n🌐 Starting server at http://127.0.0.1:8050")
        print("🎯 @role_required('admin') decorator bypassed")
        print("🔓 Authentication disabled for development")
        print("🛡️ CSRF protection disabled")
        print("🔧 LazyString issues resolved")
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
        
        if "SchemaLengthValidationError" in str(e):
            print("\n💡 Still getting callback errors:")
            print("The @role_required decorator may not be fully bypassed")
            print("Check that DISABLE_AUTH=True is set in environment")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())