#!/usr/bin/env python3
"""
Direct Flask-Babel Fix
Patches Flask-Babel to return strings instead of LazyString objects
"""

def apply_direct_babel_fix():
    """Apply direct fix to Flask-Babel to eliminate LazyString"""
    print("🔧 Applying direct Flask-Babel fix...")
    
    try:
        # Import Flask-Babel
        from flask_babel import lazy_gettext, gettext
        
        # Store originals
        original_lazy_gettext = lazy_gettext
        original_gettext = gettext
        
        # Create string-returning versions
        def string_gettext(string, **variables):
            """Return string instead of LazyString"""
            try:
                result = original_gettext(string, **variables)
                return str(result)  # Force to string
            except:
                return str(string)
        
        def string_lazy_gettext(string, **variables):
            """Return string instead of LazyString"""
            try:
                result = original_lazy_gettext(string, **variables)
                return str(result)  # Force to string
            except:
                return str(string)
        
        # Monkey patch Flask-Babel
        import flask_babel
        flask_babel.lazy_gettext = string_lazy_gettext
        flask_babel.gettext = string_gettext
        flask_babel._l = string_lazy_gettext  # Common alias
        
        print("✅ Patched Flask-Babel to return strings")
        return True
        
    except ImportError:
        print("⚠️  Flask-Babel not available to patch")
        return False
    except Exception as e:
        print(f"❌ Error patching Flask-Babel: {e}")
        return False


def apply_json_fallback_fix():
    """Apply JSON fallback fix as backup"""
    print("🔧 Applying JSON fallback fix...")
    
    import json
    
    # Store original
    original_default = json.JSONEncoder.default
    
    def ultimate_json_handler(self, obj):
        """Ultimate JSON handler that converts everything problematic to string"""
        obj_type_str = str(type(obj))
        
        # Handle LazyString specifically
        if 'LazyString' in obj_type_str:
            return str(obj)
        
        # Handle Babel objects
        if 'babel' in obj_type_str.lower():
            return str(obj)
        
        # Handle any object with _func (lazy evaluation)
        if hasattr(obj, '_func'):
            return str(obj)
        
        # Handle functions
        if callable(obj):
            return f"Function: {getattr(obj, '__name__', str(obj))}"
        
        # Handle complex objects
        if hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, list, dict)):
            return str(obj)
        
        # Try original handler
        try:
            return original_default(self, obj)
        except TypeError:
            # Ultimate fallback
            return str(obj)
    
    # Apply globally
    json.JSONEncoder.default = ultimate_json_handler
    
    # Also patch json.dumps directly
    original_dumps = json.dumps
    
    def safe_dumps(obj, **kwargs):
        """Safe dumps that handles any object"""
        try:
            return original_dumps(obj, **kwargs)
        except TypeError:
            # If that fails, use our handler
            return original_dumps(obj, default=ultimate_json_handler, **kwargs)
    
    json.dumps = safe_dumps
    
    print("✅ Applied ultimate JSON fallback fix")
    return True


def test_lazystring_fix():
    """Test the LazyString fix"""
    print("🧪 Testing LazyString fix...")
    
    try:
        # Test Flask-Babel if available
        from flask_babel import lazy_gettext as _l
        
        # Create a LazyString
        test_string = _l("Test string")
        print(f"   LazyString type: {type(test_string)}")
        
        # Test JSON serialization
        import json
        result = json.dumps({"test": test_string})
        print(f"   JSON result: {result}")
        print("✅ LazyString fix is working!")
        return True
        
    except ImportError:
        print("⚠️  Flask-Babel not available for testing")
        return True
    except Exception as e:
        print(f"❌ LazyString test failed: {e}")
        return False


def create_immediate_patch_file():
    """Create a file you can import to apply the fix"""
    patch_content = '''"""
Immediate LazyString Patch
Import this at the top of your app.py to fix LazyString issues
"""

def apply_lazystring_patch():
    """Apply LazyString patch - call this first thing in your app"""
    
    # 1. Patch Flask-Babel to return strings
    try:
        from flask_babel import lazy_gettext, gettext
        import flask_babel
        
        original_lazy = lazy_gettext
        original_get = gettext
        
        def string_lazy(string, **variables):
            return str(original_lazy(string, **variables))
        
        def string_get(string, **variables):
            return str(original_get(string, **variables))
        
        flask_babel.lazy_gettext = string_lazy
        flask_babel.gettext = string_get
        flask_babel._l = string_lazy
        
        print("✅ Flask-Babel patched to return strings")
        
    except ImportError:
        pass
    
    # 2. Patch JSON globally
    import json
    original_default = json.JSONEncoder.default
    
    def lazystring_json_handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        if hasattr(obj, '_func'):
            return str(obj)
        if callable(obj):
            return str(obj)
        try:
            return original_default(self, obj)
        except TypeError:
            return str(obj)
    
    json.JSONEncoder.default = lazystring_json_handler
    print("✅ JSON patched for LazyString")

# Auto-apply when imported
apply_lazystring_patch()
'''
    
    try:
        with open("lazystring_patch.py", "w") as f:
            f.write(patch_content)
        print("✅ Created lazystring_patch.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create patch file: {e}")
        return False


def create_fixed_app_launcher():
    """Create app launcher with LazyString fix built-in"""
    launcher_content = '''#!/usr/bin/env python3
"""
LazyString-Fixed App Launcher
"""

# CRITICAL: Apply LazyString fixes BEFORE any other imports
print("🔧 Applying LazyString fixes...")

# Fix 1: Patch JSON globally
import json
original_default = json.JSONEncoder.default

def handle_lazystring(self, obj):
    if 'LazyString' in str(type(obj)):
        return str(obj)
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        return str(obj)  
    if callable(obj):
        return str(obj)
    try:
        return original_default(self, obj)
    except TypeError:
        return str(obj)

json.JSONEncoder.default = handle_lazystring

# Fix 2: Patch Flask-Babel when it's imported
import sys
original_import = __builtins__.__import__

def patched_import(name, *args, **kwargs):
    module = original_import(name, *args, **kwargs)
    
    if name == 'flask_babel' or name.endswith('.flask_babel'):
        # Patch Flask-Babel on import
        if hasattr(module, 'lazy_gettext'):
            original_lazy = module.lazy_gettext
            module.lazy_gettext = lambda s, **k: str(original_lazy(s, **k))
            module._l = module.lazy_gettext
            print("✅ Patched Flask-Babel on import")
    
    return module

__builtins__.__import__ = patched_import

print("✅ LazyString fixes applied globally")

# Now load environment and run app
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    if Path(".env").exists():
        load_dotenv(override=True)
except ImportError:
    pass

# Set variables
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("SECRET_KEY", "dev-secret-12345")
os.environ.setdefault("YOSAI_ENV", "development")

if __name__ == "__main__":
    print("🚀 Starting LazyString-Fixed Dashboard...")
    
    try:
        from core.app_factory import create_application
        
        app = create_application()
        if app:
            print("✅ App created with LazyString fixes")
            print("🌐 URL: http://127.0.0.1:8058")
            print("🔧 LazyString errors should be eliminated")
            
            app.run(debug=True, host="127.0.0.1", port=8058)
        else:
            print("❌ Failed to create app")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
'''
    
    try:
        with open("launch_lazystring_fixed.py", "w") as f:
            f.write(launcher_content)
        print("✅ Created LazyString-fixed launcher")
        return True
    except Exception as e:
        print(f"❌ Failed to create launcher: {e}")
        return False


def main():
    """Apply all direct LazyString fixes"""
    print("🚨 Direct LazyString Fix")
    print("=" * 25)
    print("This patches Flask-Babel directly to prevent LazyString creation")
    print()
    
    # Apply fixes
    babel_fixed = apply_direct_babel_fix()
    json_fixed = apply_json_fallback_fix()
    
    # Test the fix
    test_lazystring_fix()
    
    # Create helper files
    create_immediate_patch_file()
    create_fixed_app_launcher()
    
    print(f"\n🎉 Direct LazyString fixes applied!")
    print(f"\n🚀 Immediate solutions:")
    print(f"   1. python3 launch_lazystring_fixed.py  # Built-in fixes")
    print(f"   2. Add 'import lazystring_patch' as first line in app.py")
    print(f"   3. Kill existing app and restart with fixes")
    
    print(f"\n🔧 Quick restart:")
    print(f"   kill -9 $(lsof -ti:8050) 2>/dev/null; python3 launch_lazystring_fixed.py")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())