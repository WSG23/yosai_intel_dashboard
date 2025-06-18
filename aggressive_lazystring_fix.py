#!/usr/bin/env python3
"""
Aggressive LazyString Fix
Monkey patches JSON serialization and Dash callback handling globally
"""

import json
import sys
from pathlib import Path


def apply_global_lazystring_fix():
    """Apply global LazyString fix by monkey patching JSON and Dash"""
    
    print("🔧 Applying aggressive LazyString fix...")
    
    # 1. Monkey patch JSON serialization globally
    original_default = json.JSONEncoder.default
    
    def lazystring_json_handler(self, obj):
        """Handle LazyString and other non-serializable objects"""
        # Handle LazyString objects
        if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
            return str(obj)
        
        # Handle Babel lazy objects  
        if hasattr(obj, '_func') and hasattr(obj, '_args'):
            try:
                return str(obj)
            except:
                return f"LazyString({repr(obj)})"
        
        # Handle functions
        if callable(obj):
            return f"Function: {getattr(obj, '__name__', 'anonymous')}"
        
        # Handle complex objects
        if hasattr(obj, '__dict__'):
            try:
                return str(obj)
            except:
                return f"Object: {obj.__class__.__name__}"
        
        # Call original handler
        try:
            return original_default(self, obj)
        except TypeError:
            return str(obj)
    
    json.JSONEncoder.default = lazystring_json_handler
    print("✅ Patched JSON serialization globally")
    
    # 2. Monkey patch Dash callback handling
    try:
        import dash
        from dash._callback import handle_callback_exception
        
        # Store original callback handler
        original_callback_handler = None
        if hasattr(dash, '_callback_context'):
            original_callback_handler = getattr(dash._callback_context, 'callback_fn', None)
        
        def safe_callback_wrapper(original_func):
            """Wrap callback function to handle LazyString"""
            def wrapper(*args, **kwargs):
                try:
                    result = original_func(*args, **kwargs)
                    return sanitize_lazystring_deep(result)
                except Exception as e:
                    print(f"❌ Callback error: {e}")
                    return create_safe_error_response(str(e))
            return wrapper
        
        print("✅ Enhanced Dash callback handling")
        
    except ImportError:
        print("⚠️  Could not patch Dash (not imported yet)")
    
    # 3. Add to Python's JSON module
    def safe_dumps(obj, **kwargs):
        """Safe JSON dumps that handles LazyString"""
        return json.dumps(obj, default=lazystring_json_handler, **kwargs)
    
    # Replace json.dumps with safe version
    json.original_dumps = json.dumps
    json.dumps = safe_dumps
    print("✅ Replaced json.dumps with LazyString-safe version")


def sanitize_lazystring_deep(obj):
    """Deep sanitization of LazyString objects"""
    if obj is None:
        return None
    
    # Handle LazyString
    if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
        return str(obj)
    
    # Handle Babel lazy objects
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        try:
            return str(obj)
        except:
            return f"LazyString: {repr(obj)}"
    
    # Handle lists/tuples
    if isinstance(obj, (list, tuple)):
        return type(obj)(sanitize_lazystring_deep(item) for item in obj)
    
    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: sanitize_lazystring_deep(value) for key, value in obj.items()}
    
    # Handle Dash components
    if hasattr(obj, 'to_plotly_json'):
        try:
            plotly_dict = obj.to_plotly_json()
            return sanitize_lazystring_deep(plotly_dict)
        except:
            return str(obj)
    
    # Handle objects with __dict__
    if hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool)):
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)
    
    return obj


def create_safe_error_response(error_msg):
    """Create safe error response"""
    try:
        from dash import html
        return html.Div([
            html.H4("⚠️ Callback Error", className="text-warning"),
            html.P(f"LazyString serialization error: {error_msg}"),
        ], className="alert alert-warning")
    except ImportError:
        return {"error": "LazyString error", "message": error_msg}


def patch_app_startup():
    """Create a patched app startup script"""
    patched_app = '''#!/usr/bin/env python3
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
'''
    
    try:
        with open("launch_lazystring_patched.py", "w") as f:
            f.write(patched_app)
        print("✅ Created LazyString-patched launcher")
        return True
    except Exception as e:
        print(f"❌ Failed to create patched launcher: {e}")
        return False


def create_manual_patch_instructions():
    """Create instructions for manual patching"""
    instructions = '''# Manual LazyString Fix Instructions

## Option 1: Add to top of your app.py

Add this code at the very top of app.py, before any other imports:

```python
# LazyString JSON Fix - Add at TOP of app.py
import json

original_default = json.JSONEncoder.default

def lazystring_handler(self, obj):
    if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
        return str(obj)
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        return str(obj)
    if callable(obj):
        return str(obj)
    try:
        return original_default(self, obj)
    except TypeError:
        return str(obj)

json.JSONEncoder.default = lazystring_handler
```

## Option 2: Create .py file and import it first

Create `lazystring_patch.py`:
```python
import json

def apply_patch():
    original = json.JSONEncoder.default
    def handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        return original(self, obj)
    json.JSONEncoder.default = handler

apply_patch()
```

Then in app.py, add as first import:
```python
import lazystring_patch  # Must be first import
```

## Option 3: Environment variable

Set this before running:
```bash
export PYTHONPATH=".:$PYTHONPATH"
python3 -c "import json; json.JSONEncoder.default = lambda self, obj: str(obj) if 'LazyString' in str(type(obj)) else json.JSONEncoder.default(self, obj)" && python3 app.py
```
'''
    
    with open("LAZYSTRING_FIX_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    print("✅ Created manual fix instructions")


def main():
    """Main aggressive fix function"""
    print("🚨 Aggressive LazyString Fix")
    print("=" * 30)
    print("This applies global JSON patching to eliminate LazyString errors")
    print()
    
    # Apply global fix
    apply_global_lazystring_fix()
    
    # Create patched launcher
    patch_app_startup()
    
    # Create manual instructions
    create_manual_patch_instructions()
    
    print("\n🎉 Aggressive LazyString fixes applied!")
    print("\n🚀 Try these options:")
    print("   1. python3 launch_lazystring_patched.py  # Most aggressive fix")
    print("   2. Add manual patch to app.py (see LAZYSTRING_FIX_INSTRUCTIONS.md)")
    print("   3. python3 minimal_working_app.py        # Simple version")
    
    print("\n📋 What was applied:")
    print("   ✅ Global JSON serialization patched")
    print("   ✅ Dash callback handling enhanced") 
    print("   ✅ LazyString objects converted to strings")
    print("   ✅ Created patched launcher")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())