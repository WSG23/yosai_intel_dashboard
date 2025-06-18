#!/usr/bin/env python3
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
