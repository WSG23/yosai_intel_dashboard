#!/usr/bin/env python3
"""
Complete Final Setup for Yosai Dashboard
Fixes the remaining 3 issues found by diagnostic

Run this to complete the setup process.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_flask_babel():
    """Install flask-babel dependency"""
    print("📦 Installing flask-babel...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'flask-babel>=4.0.0'
        ], capture_output=True, text=True, check=True)
        print("✅ flask-babel installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install flask-babel: {e}")
        print(f"Error: {e.stderr}")
        return False


def create_env_file():
    """Create/update .env file with AUTH0 variables"""
    print("📝 Setting up environment variables...")
    
    env_additions = """
# Auth0 Configuration (Development - safe defaults)
AUTH0_CLIENT_ID=dev-client-id-12345
AUTH0_CLIENT_SECRET=dev-client-secret-12345
AUTH0_DOMAIN=dev-domain.auth0.com

# Core Flask/Yosai Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
YOSAI_ENV=development
WTF_CSRF_ENABLED=False
DB_HOST=localhost
"""
    
    env_file = Path('.env')
    
    # Read existing content if file exists
    existing_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            existing_content = f.read()
    
    # Add new variables if they don't already exist
    lines_to_add = []
    for line in env_additions.strip().split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            var_name = line.split('=')[0].strip()
            if var_name not in existing_content:
                lines_to_add.append(line)
    
    if lines_to_add:
        with open(env_file, 'a') as f:
            f.write('\n' + '\n'.join(lines_to_add) + '\n')
        print(f"✅ Added {len(lines_to_add)} environment variables to .env")
    else:
        print("✅ Environment variables already set")
    
    return True


def create_lazystring_plugin():
    """Create the LazyString plugin file"""
    print("🔧 Creating LazyString plugin...")
    
    plugin_content = '''#!/usr/bin/env python3
"""
LazyString Serialization Plugin for Flask-Babel Applications
Comprehensive solution for handling LazyString JSON serialization errors
"""

import json
import logging
import functools
import sys
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager


class LazyStringSerializationPlugin:
    """Plugin to handle Flask-Babel LazyString serialization issues"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.original_json_default = None
        self.original_babel_functions = {}
        self.is_active = False
        self.config = {
            'auto_patch_babel': True,
            'auto_patch_json': True,
            'force_string_conversion': True,
            'fallback_to_repr': True,
            'debug_mode': False
        }
    
    def activate(self, **config_overrides) -> bool:
        """Activate the LazyString plugin with optional configuration"""
        try:
            # Update configuration
            self.config.update(config_overrides)
            
            if self.config['debug_mode']:
                self.logger.setLevel(logging.DEBUG)
            
            self.logger.info("🔧 Activating LazyString Serialization Plugin...")
            
            # Apply patches
            patches_applied = 0
            
            if self.config['auto_patch_babel']:
                if self._patch_flask_babel():
                    patches_applied += 1
                    
            if self.config['auto_patch_json']:
                if self._patch_json_encoder():
                    patches_applied += 1
            
            self.is_active = patches_applied > 0
            
            if self.is_active:
                self.logger.info(f"✅ Plugin activated with {patches_applied} patches applied")
            else:
                self.logger.warning("⚠️ Plugin activation failed - no patches applied")
                
            return self.is_active
            
        except Exception as e:
            self.logger.error(f"❌ Plugin activation failed: {e}")
            return False
    
    def _patch_flask_babel(self) -> bool:
        """Patch Flask-Babel to return strings instead of LazyString objects"""
        try:
            import flask_babel
            
            # Store original functions if not already stored
            if not self.original_babel_functions:
                self.original_babel_functions = {
                    'lazy_gettext': flask_babel.lazy_gettext,
                    'gettext': flask_babel.gettext,
                }
                
                # Store _l if it exists
                if hasattr(flask_babel, '_l'):
                    self.original_babel_functions['_l'] = flask_babel._l
            
            # Create string-returning wrapper functions
            def string_lazy_gettext(string, **variables):
                """Wrapper that ensures string return from lazy_gettext"""
                try:
                    result = self.original_babel_functions['lazy_gettext'](string, **variables)
                    return str(result) if self.config['force_string_conversion'] else result
                except Exception as e:
                    self.logger.debug(f"lazy_gettext conversion error: {e}")
                    return str(string)
            
            def string_gettext(string, **variables):
                """Wrapper that ensures string return from gettext"""
                try:
                    result = self.original_babel_functions['gettext'](string, **variables)
                    return str(result) if self.config['force_string_conversion'] else result
                except Exception as e:
                    self.logger.debug(f"gettext conversion error: {e}")
                    return str(string)
            
            # Apply patches
            flask_babel.lazy_gettext = string_lazy_gettext
            flask_babel.gettext = string_gettext
            flask_babel._l = string_lazy_gettext  # Common alias
            
            self.logger.info("✅ Flask-Babel patched successfully")
            return True
            
        except ImportError:
            self.logger.warning("⚠️ Flask-Babel not available - skipping Babel patch")
            return False
        except Exception as e:
            self.logger.error(f"❌ Flask-Babel patching failed: {e}")
            return False
    
    def _patch_json_encoder(self) -> bool:
        """Patch JSON encoder to handle LazyString and other problematic objects"""
        try:
            # Store original if not already stored
            if not self.original_json_default:
                self.original_json_default = json.JSONEncoder.default
            
            def enhanced_json_handler(self, obj):
                """Enhanced JSON handler for LazyString and other objects"""
                obj_type_str = str(type(obj))
                
                # Handle LazyString specifically
                if 'LazyString' in obj_type_str:
                    return str(obj)
                
                # Handle Babel objects
                if 'babel' in obj_type_str.lower():
                    return str(obj)
                
                # Handle lazy evaluation objects
                if hasattr(obj, '_func') and hasattr(obj, '_args'):
                    return str(obj)
                
                # Handle callable objects
                if callable(obj):
                    func_name = getattr(obj, '__name__', 'anonymous_function')
                    return f"Function: {func_name}"
                
                # Handle complex objects with __dict__
                if (hasattr(obj, '__dict__') and 
                    not isinstance(obj, (str, int, float, bool, list, dict))):
                    if self.config['fallback_to_repr']:
                        return repr(obj)
                    else:
                        return f"Object: {obj.__class__.__name__}"
                
                # Try original handler
                try:
                    return self.original_json_default(self, obj)
                except (TypeError, AttributeError):
                    # Handle case where original handler expects 'config' attribute
                    # This happens with custom encoders like YosaiJSONEncoder
                    if hasattr(self, 'config'):
                        # Try to call with config
                        try:
                            import inspect
                            sig = inspect.signature(self.original_json_default)
                            if 'config' in sig.parameters:
                                return str(obj)  # Fallback for config-based encoders
                        except:
                            pass
                    # Ultimate fallback
                    return str(obj) if self.config['fallback_to_repr'] else None
            
            # Apply patch
            json.JSONEncoder.default = enhanced_json_handler
            
            self.logger.info("✅ JSON encoder patched successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ JSON encoder patching failed: {e}")
            return False
    
    def test_functionality(self) -> Dict[str, bool]:
        """Test plugin functionality"""
        results = {
            'plugin_active': self.is_active,
            'babel_patch_test': False,
            'json_patch_test': False,
            'sanitization_test': False
        }
        
        # Test Flask-Babel patching
        try:
            from flask_babel import lazy_gettext as _l
            test_string = _l("Test string")
            json.dumps({"test": test_string})
            results['babel_patch_test'] = True
        except Exception as e:
            self.logger.debug(f"Babel patch test failed: {e}")
        
        # Test JSON patching
        try:
            class TestLazyObject:
                def __init__(self):
                    self._func = lambda: "test"
                    self._args = ()
                def __str__(self):
                    return "TestLazyObject"
            
            test_obj = TestLazyObject()
            json.dumps({"test": test_obj})
            results['json_patch_test'] = True
        except Exception as e:
            self.logger.debug(f"JSON patch test failed: {e}")
        
        # Test sanitization
        try:
            test_data = {"func": lambda x: x, "normal": "string"}
            sanitized = self.sanitize_data(test_data)
            json.dumps(sanitized)
            results['sanitization_test'] = True
        except Exception as e:
            self.logger.debug(f"Sanitization test failed: {e}")
        
        return results
    
    def sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize data to ensure JSON serializability"""
        if data is None:
            return None
        
        # Handle LazyString objects
        if hasattr(data, '__class__') and 'LazyString' in str(data.__class__):
            return str(data)
        
        # Handle lazy evaluation objects
        if hasattr(data, '_func') and hasattr(data, '_args'):
            return str(data)
        
        # Handle lists and tuples
        if isinstance(data, (list, tuple)):
            return type(data)(self.sanitize_data(item) for item in data)
        
        # Handle dictionaries
        if isinstance(data, dict):
            return {key: self.sanitize_data(value) for key, value in data.items()}
        
        # Handle objects with __dict__
        if (hasattr(data, '__dict__') and 
            not isinstance(data, (str, int, float, bool))):
            try:
                # Test if already serializable
                json.dumps(data, default=str)
                return data
            except (TypeError, ValueError):
                return {
                    'type': data.__class__.__name__,
                    'representation': str(data)
                }
        
        return data


# Global plugin instance
lazystring_plugin = LazyStringSerializationPlugin()


def apply_lazystring_fixes(**config_overrides) -> bool:
    """Convenience function to apply LazyString fixes"""
    return lazystring_plugin.activate(**config_overrides)


def remove_lazystring_fixes() -> bool:
    """Convenience function to remove LazyString fixes"""
    return lazystring_plugin.deactivate()


if __name__ == "__main__":
    # Test the plugin when run directly
    print("🧪 Testing LazyString Serialization Plugin...")
    
    # Activate plugin
    success = apply_lazystring_fixes(debug_mode=True)
    print(f"Plugin activation: {'✅ Success' if success else '❌ Failed'}")
    
    # Run tests
    test_results = lazystring_plugin.test_functionality()
    print("\\nTest Results:")
    for test_name, result in test_results.items():
        status = "✅ Pass" if result else "❌ Fail"
        print(f"  {test_name}: {status}")
'''
    
    plugin_file = Path('lazystring_plugin.py')
    with open(plugin_file, 'w') as f:
        f.write(plugin_content)
    
    print(f"✅ Created {plugin_file}")
    return True


def test_final_setup():
    """Test that everything is working"""
    print("🧪 Testing final setup...")
    
    try:
        # Test flask-babel import
        import flask_babel
        print("✅ flask-babel import successful")
        
        # Test LazyString plugin
        from lazystring_plugin import apply_lazystring_fixes
        print("✅ LazyString plugin import successful")
        
        # Test environment variables
        import os
        from dotenv import load_dotenv
        
        if Path('.env').exists():
            load_dotenv()
        
        auth_id = os.getenv('AUTH0_CLIENT_ID')
        if auth_id:
            print(f"✅ AUTH0_CLIENT_ID found: {auth_id}")
        else:
            print("⚠️ AUTH0_CLIENT_ID not found in environment")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def main():
    """Complete the final setup"""
    print("🎯 Final Setup for Yosai Dashboard")
    print("=" * 40)
    print("Fixing the last 3 issues...\n")
    
    success_count = 0
    
    # Step 1: Install flask-babel
    if install_flask_babel():
        success_count += 1
    print()
    
    # Step 2: Create/update .env file
    if create_env_file():
        success_count += 1
    print()
    
    # Step 3: Create LazyString plugin
    if create_lazystring_plugin():
        success_count += 1
    print()
    
    # Step 4: Test everything
    if test_final_setup():
        success_count += 1
    print()
    
    # Final report
    print("📊 Final Setup Results")
    print("-" * 25)
    print(f"Completed: {success_count}/4 steps")
    
    if success_count == 4:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Ready to run:")
        print("1. python3 app_diagnostic.py  # Should show no issues")
        print("2. python3 app_launcher.py --mode protected")
        print("\n📍 Your app will be available at: http://127.0.0.1:8050")
        return 0
    else:
        print("⚠️ Some steps failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())