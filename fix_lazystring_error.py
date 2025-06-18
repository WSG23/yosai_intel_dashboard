#!/usr/bin/env python3
"""
Fix LazyString JSON Serialization Error
Handles Flask-Babel LazyString objects that aren't JSON serializable
"""

import json
import functools
from typing import Any
from pathlib import Path


class LazyStringHandler:
    """Handle Flask-Babel LazyString serialization issues"""
    
    def __init__(self):
        self.fixes_applied = []
    
    def sanitize_lazystring(self, obj: Any) -> Any:
        """Convert LazyString objects to regular strings"""
        
        # Handle LazyString objects
        if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
            return str(obj)
        
        # Handle lists/tuples
        if isinstance(obj, (list, tuple)):
            return type(obj)(self.sanitize_lazystring(item) for item in obj)
        
        # Handle dictionaries
        if isinstance(obj, dict):
            return {key: self.sanitize_lazystring(value) for key, value in obj.items()}
        
        # Handle other objects with LazyString attributes
        if hasattr(obj, '__dict__'):
            # Don't modify the original object, create a safe representation
            try:
                # Test if it's JSON serializable first
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # If not serializable, create safe dict representation
                safe_dict = {}
                for key, value in obj.__dict__.items():
                    try:
                        safe_dict[key] = self.sanitize_lazystring(value)
                    except:
                        safe_dict[key] = str(value)
                return safe_dict
        
        return obj
    
    def create_lazystring_safe_wrapper(self) -> bool:
        """Create a wrapper that handles LazyString in callbacks"""
        try:
            wrapper_content = '''#!/usr/bin/env python3
"""
LazyString Safe Wrapper
Handles Flask-Babel LazyString objects in Dash callbacks
"""

import json
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def sanitize_lazystring_recursive(obj: Any) -> Any:
    """Recursively sanitize LazyString objects"""
    
    # Handle LazyString objects (from Flask-Babel)
    if hasattr(obj, '__class__') and 'LazyString' in str(obj.__class__):
        return str(obj)
    
    # Handle Babel lazy objects
    if hasattr(obj, '_func') and hasattr(obj, '_args'):
        # This looks like a lazy evaluation object
        try:
            return str(obj)
        except:
            return f"LazyString: {repr(obj)}"
    
    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        return type(obj)(sanitize_lazystring_recursive(item) for item in obj)
    
    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: sanitize_lazystring_recursive(value) for key, value in obj.items()}
    
    # Handle Dash components with LazyString properties
    if hasattr(obj, 'children') and hasattr(obj, 'to_plotly_json'):
        # This is likely a Dash component
        try:
            # Try to serialize as-is first
            json.dumps(obj.to_plotly_json())
            return obj
        except (TypeError, ValueError):
            # Component has LazyString properties, sanitize them
            component_dict = obj.to_plotly_json()
            return sanitize_lazystring_recursive(component_dict)
    
    # Handle objects with LazyString attributes
    if hasattr(obj, '__dict__'):
        try:
            # Test if already serializable
            json.dumps(obj, default=str)
            return obj
        except:
            # Create safe representation
            return {
                'type': obj.__class__.__name__,
                'str_repr': str(obj)
            }
    
    # For primitive types, return as-is
    return obj


def lazystring_safe_callback(func: Callable) -> Callable:
    """Decorator to make callbacks safe from LazyString serialization errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute original callback
            result = func(*args, **kwargs)
            
            # Sanitize LazyString objects in the result
            sanitized_result = sanitize_lazystring_recursive(result)
            
            # Test final serialization
            try:
                json.dumps(sanitized_result, default=str)
                return sanitized_result
            except:
                # Ultimate fallback
                return str(sanitized_result)
                
        except Exception as e:
            logger.error(f"LazyString callback {func.__name__} failed: {e}")
            
            # Return safe error component
            try:
                from dash import html
                return html.Div([
                    html.H4("⚠️ Translation Error", className="text-warning"),
                    html.P(f"Callback: {func.__name__}"),
                    html.P(f"LazyString serialization error"),
                ], className="alert alert-warning")
            except ImportError:
                return {"error": "LazyString serialization error", "callback": func.__name__}
    
    return wrapper


# Export for easy importing
__all__ = ['lazystring_safe_callback', 'sanitize_lazystring_recursive']
'''
            
            with open("utils/lazystring_handler.py", "w") as f:
                f.write(wrapper_content)
            
            print("✅ Created LazyString safe wrapper")
            self.fixes_applied.append("Created LazyString handler")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create LazyString wrapper: {e}")
            return False
    
    def patch_babel_usage(self) -> bool:
        """Find and patch files that use Flask-Babel _l() function"""
        
        # Files that likely use _l() for translations
        files_to_check = [
            "dashboard/layout/navbar.py",
            "components/navbar.py", 
            "pages/deep_analytics.py",
            "components/analytics/",
        ]
        
        patches_applied = []
        
        for file_path in files_to_check:
            path = Path(file_path)
            
            if path.is_file():
                if self._patch_file_for_lazystring(path):
                    patches_applied.append(str(path))
            elif path.is_dir():
                for py_file in path.glob("**/*.py"):
                    if self._patch_file_for_lazystring(py_file):
                        patches_applied.append(str(py_file))
        
        if patches_applied:
            print(f"✅ Patched {len(patches_applied)} files for LazyString")
            self.fixes_applied.extend(patches_applied)
        else:
            print("📋 No files needed LazyString patching")
        
        return True
    
    def _patch_file_for_lazystring(self, file_path: Path) -> bool:
        """Patch a single file for LazyString issues"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Skip files that don't use _l()
            if '_l(' not in content:
                return False
            
            # Backup original
            backup_path = f"{file_path}.lazystring_backup"
            with open(backup_path, 'w') as f:
                f.write(content)
            
            # Add import for LazyString handler
            if "from utils.lazystring_handler import" not in content:
                lines = content.split('\n')
                
                # Find import section
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_index = i
                
                # Add LazyString handler import
                lines.insert(import_index + 1, "from utils.lazystring_handler import sanitize_lazystring_recursive")
                
                # Wrap any function that returns _l() strings
                for i, line in enumerate(lines):
                    if 'return ' in line and '_l(' in line:
                        lines[i] = line.replace('return ', 'return str(') + ')'
                
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"   ✅ Patched {file_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Error patching {file_path}: {e}")
            return False
    
    def update_callback_manager(self) -> bool:
        """Update CallbackManager to use LazyString-safe decorators"""
        file_path = Path("core/callback_manager.py")
        
        if not file_path.exists():
            print("📋 CallbackManager not found - skipping")
            return True
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add LazyString handler import
            if "from utils.lazystring_handler import lazystring_safe_callback" not in content:
                # Backup
                with open("core/callback_manager.py.lazystring_backup", 'w') as f:
                    f.write(content)
                
                lines = content.split('\n')
                
                # Add import
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        lines.insert(i + 1, "from utils.lazystring_handler import lazystring_safe_callback")
                        break
                
                # Wrap callback registrations
                for i, line in enumerate(lines):
                    if '@self.app.callback' in line:
                        # Add LazyString safety wrapper before the callback
                        indent = line[:len(line) - len(line.lstrip())]
                        lines.insert(i + 1, f"{indent}@lazystring_safe_callback")
                
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Updated CallbackManager for LazyString safety")
                self.fixes_applied.append("Updated CallbackManager")
                return True
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update CallbackManager: {e}")
            return False
    
    def create_fixed_debug_script(self) -> bool:
        """Create debug script that handles LazyString"""
        try:
            fixed_debug = '''#!/usr/bin/env python3
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
'''
            
            with open("launch_lazystring_safe.py", "w") as f:
                f.write(fixed_debug)
            
            print("✅ Created LazyString-safe launcher")
            self.fixes_applied.append("Created LazyString-safe launcher")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create LazyString-safe launcher: {e}")
            return False
    
    def apply_all_lazystring_fixes(self) -> bool:
        """Apply all LazyString fixes"""
        print("🔧 Fixing LazyString JSON Serialization Issues")
        print("=" * 50)
        print("Flask-Babel LazyString objects need special handling for JSON serialization")
        print()
        
        fixes = [
            ("Creating LazyString safe wrapper", self.create_lazystring_safe_wrapper),
            ("Patching Babel usage", self.patch_babel_usage),
            ("Updating CallbackManager", self.update_callback_manager),
            ("Creating LazyString-safe launcher", self.create_fixed_debug_script),
        ]
        
        all_successful = True
        for fix_name, fix_func in fixes:
            print(f"🔧 {fix_name}...")
            if not fix_func():
                all_successful = False
                print(f"❌ {fix_name} failed")
            else:
                print(f"✅ {fix_name} completed")
        
        print(f"\n📊 LazyString Fix Summary")
        print("=" * 30)
        if self.fixes_applied:
            print("Fixes applied:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        if all_successful:
            print(f"\n🎉 All LazyString fixes applied!")
            print(f"\n🚀 Try these options:")
            print(f"   1. python3 launch_lazystring_safe.py  # LazyString-safe version")
            print(f"   2. python3 minimal_working_app.py     # Minimal version")
            print(f"   3. python3 app.py                    # Original (may still have LazyString issues)")
            return True
        else:
            print(f"\n❌ Some LazyString fixes failed")
            return False


def main():
    """Main LazyString fix function"""
    handler = LazyStringHandler()
    success = handler.apply_all_lazystring_fixes()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())