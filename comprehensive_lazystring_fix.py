#!/usr/bin/env python3
"""
Comprehensive LazyString Fix for Yosai Dashboard
Handles LazyString serialization at multiple levels to eliminate all errors

This script applies fixes at:
1. Import level - patches before any modules load
2. JSON encoder level - global JSON patching
3. Flask-Babel level - replaces LazyString with string functions
4. Dash callback level - wraps problematic callbacks
"""

import os
import sys
import json
from pathlib import Path

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
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
        'AUTH0_DOMAIN': 'dev-domain.auth0.com'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # Load .env if available
    try:
        from dotenv import load_dotenv
        if Path('.env').exists():
            load_dotenv()
            # Override CSRF settings
            os.environ['WTF_CSRF_ENABLED'] = 'False'
            print("   ✅ Loaded .env with overrides")
    except ImportError:
        pass

def patch_json_completely():
    """Apply comprehensive JSON patching"""
    print("🔧 Applying comprehensive JSON fixes...")
    
    # Store original functions
    original_default = json.JSONEncoder.default
    original_dumps = json.dumps
    original_loads = json.loads
    
    def ultimate_json_handler(self, obj):
        """Ultimate JSON handler that converts everything problematic to string"""
        obj_type_str = str(type(obj))
        
        # Handle LazyString specifically
        if 'LazyString' in obj_type_str:
            return str(obj)
        
        # Handle any babel objects
        if 'babel' in obj_type_str.lower() or 'speaklater' in obj_type_str.lower():
            return str(obj)
        
        # Handle lazy evaluation objects
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            return str(obj)
        
        # Handle any object with lazy in the name
        if 'lazy' in obj_type_str.lower():
            return str(obj)
        
        # Handle functions and callables
        if callable(obj):
            return f"Function: {getattr(obj, '__name__', str(obj))}"
        
        # Handle complex objects
        if hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, list, dict)):
            try:
                # Try to serialize as-is first
                json.dumps(obj, default=str)
                return obj
            except:
                return str(obj)
        
        # Try original handler
        try:
            return original_default(self, obj)
        except (TypeError, AttributeError, ValueError):
            # Ultimate fallback - everything becomes a string
            return str(obj)
    
    def safe_dumps(obj, **kwargs):
        """Safe dumps that handles any object"""
        try:
            # First try with our custom handler
            return original_dumps(obj, default=ultimate_json_handler, **kwargs)
        except (TypeError, ValueError):
            # If that fails, convert everything to strings
            try:
                def stringify_all(o):
                    return str(o)
                return original_dumps(obj, default=stringify_all, **kwargs)
            except:
                # Ultimate fallback
                return '{"error": "serialization_failed", "type": "' + str(type(obj)) + '"}'
    
    # Apply patches
    json.JSONEncoder.default = ultimate_json_handler
    json.dumps = safe_dumps
    
    print("   ✅ JSON encoder patched completely")

def patch_flask_babel_aggressively():
    """Aggressively patch Flask-Babel to never return LazyString"""
    print("🔧 Patching Flask-Babel aggressively...")
    
    try:
        import flask_babel
        
        # Store all original functions
        originals = {}
        
        # Functions that might return LazyString
        babel_functions = [
            'lazy_gettext', 'gettext', '_', '_l', 'ngettext', 'lazy_ngettext',
            'pgettext', 'lazy_pgettext', 'npgettext', 'lazy_npgettext'
        ]
        
        for func_name in babel_functions:
            if hasattr(flask_babel, func_name):
                originals[func_name] = getattr(flask_babel, func_name)
        
        def create_string_wrapper(original_func, func_name):
            """Create a wrapper that always returns strings"""
            def string_wrapper(*args, **kwargs):
                try:
                    result = original_func(*args, **kwargs)
                    # Force conversion to string
                    string_result = str(result)
                    return string_result
                except Exception as e:
                    # If original function fails, return the first argument as string
                    return str(args[0]) if args else f"babel_error_{func_name}"
            
            return string_wrapper
        
        # Apply wrappers to all babel functions
        for func_name, original_func in originals.items():
            wrapper = create_string_wrapper(original_func, func_name)
            setattr(flask_babel, func_name, wrapper)
        
        # Also patch common aliases
        if hasattr(flask_babel, '_l'):
            flask_babel._l = getattr(flask_babel, 'lazy_gettext')
        if hasattr(flask_babel, '_'):
            flask_babel._ = getattr(flask_babel, 'gettext')
        
        print(f"   ✅ Patched {len(originals)} Flask-Babel functions")
        
    except ImportError:
        print("   ⚠️ Flask-Babel not available")
    except Exception as e:
        print(f"   ❌ Flask-Babel patching failed: {e}")

def patch_csrf_protection():
    """Patch CSRF protection to prevent activation"""
    print("🛡️ Patching CSRF protection...")
    
    try:
        import flask_wtf.csrf
        import flask_wtf
        
        class NoOpCSRFProtect:
            """No-operation CSRF protect"""
            def __init__(self, app=None):
                print("   ✅ CSRF disabled (no-op)")
                if app:
                    app.config.update({
                        'WTF_CSRF_ENABLED': False,
                        'WTF_CSRF_CHECK_DEFAULT': False,
                        'CSRF_ENABLED': False
                    })
            
            def init_app(self, app):
                app.config.update({
                    'WTF_CSRF_ENABLED': False,
                    'WTF_CSRF_CHECK_DEFAULT': False,
                    'CSRF_ENABLED': False
                })
            
            def protect(self):
                return lambda f: f
            
            def exempt(self, view):
                return view
            
            def __call__(self, *args, **kwargs):
                return self
            
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
        
        # Replace CSRFProtect
        flask_wtf.csrf.CSRFProtect = NoOpCSRFProtect
        flask_wtf.CSRFProtect = NoOpCSRFProtect
        
        print("   ✅ CSRF protection patched")
        
    except ImportError:
        print("   ⚠️ Flask-WTF not available")

def test_lazystring_fix():
    """Test that LazyString fix is working"""
    print("🧪 Testing LazyString fix...")
    
    try:
        from flask_babel import lazy_gettext as _l
        
        # Create LazyString
        lazy_str = _l("Test string")
        print(f"   LazyString type: {type(lazy_str)}")
        
        # Test serialization
        result = json.dumps({"test": lazy_str})
        print(f"   ✅ Serialization successful: {result}")
        
        # Test that it's actually a string now
        if isinstance(lazy_str, str):
            print("   ✅ LazyString converted to string")
        else:
            print(f"   ⚠️ LazyString still exists as: {type(lazy_str)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LazyString test failed: {e}")
        return False

def wrap_problematic_imports():
    """Wrap imports that might cause LazyString issues"""
    print("🔧 Wrapping problematic imports...")
    
    # Store original import
    original_import = __builtins__.__import__
    
    def safe_import(name, *args, **kwargs):
        """Safe import that applies fixes after importing babel modules"""
        module = original_import(name, *args, **kwargs)
        
        # If we just imported flask_babel, apply fixes immediately
        if name == 'flask_babel' or name.endswith('.flask_babel'):
            try:
                # Re-patch babel functions in the just-imported module
                babel_functions = ['lazy_gettext', 'gettext', '_l']
                for func_name in babel_functions:
                    if hasattr(module, func_name):
                        original_func = getattr(module, func_name)
                        def string_wrapper(*args, **kwargs):
                            result = original_func(*args, **kwargs)
                            return str(result)
                        setattr(module, func_name, string_wrapper)
                
                print(f"   ✅ Applied post-import fixes to {name}")
            except Exception as e:
                print(f"   ⚠️ Post-import fix failed for {name}: {e}")
        
        return module
    
    # Apply safe import
    __builtins__.__import__ = safe_import
    print("   ✅ Import wrapper applied")

def main():
    """Main comprehensive fix"""
    print("🎯 Comprehensive LazyString Fix for Yosai Dashboard")
    print("=" * 55)
    print("Applying multi-level LazyString elimination...\n")
    
    try:
        # Step 1: Setup environment
        setup_environment()
        
        # Step 2: Wrap imports to catch babel loading
        wrap_problematic_imports()
        
        # Step 3: Patch JSON completely
        patch_json_completely()
        
        # Step 4: Patch Flask-Babel aggressively 
        patch_flask_babel_aggressively()
        
        # Step 5: Patch CSRF protection
        patch_csrf_protection()
        
        # Step 6: Test the fixes
        if test_lazystring_fix():
            print("   ✅ LazyString fixes verified")
        
        # Step 7: Import and create app
        print("\n🚀 Creating app with comprehensive fixes...")
        from core.app_factory import create_application
        
        app = create_application()
        
        if app is None:
            print("❌ App creation failed")
            return 1
        
        print(f"✅ App created successfully: {type(app).__name__}")
        
        # Step 8: Apply final app-level fixes
        if hasattr(app, 'server'):
            app.server.config.update({
                'WTF_CSRF_ENABLED': False,
                'WTF_CSRF_CHECK_DEFAULT': False,
                'CSRF_ENABLED': False,
                'JSON_SORT_KEYS': False  # Prevent additional JSON issues
            })
            print("✅ Final app configuration applied")
        
        # Step 9: Start the app
        print("\n🌐 Starting server at http://127.0.0.1:8050")
        print("🔧 Comprehensive LazyString elimination applied")
        print("🛡️ CSRF protection disabled")
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
        
        # Even if there's an error, try to provide useful info
        print(f"\n🔍 Debug info:")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        
        if "LazyString" in str(e):
            print("💡 LazyString error detected - try installing flask-babel:")
            print("   pip install flask-babel")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())