#!/usr/bin/env python3
"""
LazyString Serialization Plugin for Flask-Babel Applications
Comprehensive solution for handling LazyString JSON serialization errors

This plugin provides:
1. Automatic Flask-Babel patching
2. JSON encoder enhancement
3. Callback decorators for Dash applications
4. Testing utilities
5. Easy integration and isolation
"""

import json
import logging
import functools
import sys
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager


class LazyStringSerializationPlugin:
    """
    Plugin to handle Flask-Babel LazyString serialization issues
    """
    
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
        """
        Activate the LazyString plugin with optional configuration
        
        Args:
            **config_overrides: Configuration options to override defaults
            
        Returns:
            bool: True if activation successful
        """
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
    
    def deactivate(self) -> bool:
        """
        Deactivate the plugin and restore original functions
        
        Returns:
            bool: True if deactivation successful
        """
        try:
            self.logger.info("🔄 Deactivating LazyString Plugin...")
            
            # Restore JSON encoder
            if self.original_json_default:
                json.JSONEncoder.default = self.original_json_default
                self.original_json_default = None
            
            # Restore Flask-Babel functions
            if self.original_babel_functions:
                import flask_babel
                for func_name, original_func in self.original_babel_functions.items():
                    setattr(flask_babel, func_name, original_func)
                self.original_babel_functions.clear()
            
            self.is_active = False
            self.logger.info("✅ Plugin deactivated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Plugin deactivation failed: {e}")
            return False
    
    def _patch_flask_babel(self) -> bool:
        """
        Patch Flask-Babel to return strings instead of LazyString objects
        
        Returns:
            bool: True if patching successful
        """
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
        """
        Patch JSON encoder to handle LazyString and other problematic objects
        
        Returns:
            bool: True if patching successful
        """
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
                except TypeError:
                    # Ultimate fallback
                    return str(obj) if self.config['fallback_to_repr'] else None
            
            # Apply patch
            json.JSONEncoder.default = enhanced_json_handler
            
            self.logger.info("✅ JSON encoder patched successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ JSON encoder patching failed: {e}")
            return False
    
    def sanitize_data(self, data: Any) -> Any:
        """
        Recursively sanitize data to ensure JSON serializability
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data safe for JSON serialization
        """
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
        
        # Handle Dash components
        if hasattr(data, 'to_plotly_json'):
            try:
                component_dict = data.to_plotly_json()
                return self.sanitize_data(component_dict)
            except Exception:
                return str(data)
        
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
    
    def safe_callback(self, func: Callable) -> Callable:
        """
        Decorator to make callbacks safe from LazyString serialization errors
        
        Args:
            func: Callback function to wrap
            
        Returns:
            Wrapped function that handles LazyString errors gracefully
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Execute original callback
                result = func(*args, **kwargs)
                
                # Sanitize result
                sanitized_result = self.sanitize_data(result)
                
                # Verify final serializability
                try:
                    json.dumps(sanitized_result)
                    return sanitized_result
                except (TypeError, ValueError):
                    self.logger.warning(f"Final serialization failed for {func.__name__}")
                    return str(sanitized_result)
                    
            except Exception as e:
                self.logger.error(f"Callback {func.__name__} failed: {e}")
                
                # Return safe fallback
                return self._create_error_component(func.__name__, str(e))
        
        return wrapper
    
    def _create_error_component(self, callback_name: str, error_msg: str) -> Union[Dict, Any]:
        """
        Create a safe error component for failed callbacks
        
        Args:
            callback_name: Name of the failed callback
            error_msg: Error message
            
        Returns:
            Safe error representation
        """
        try:
            # Try to create Dash component
            from dash import html
            return html.Div([
                html.H4("⚠️ LazyString Error", className="text-warning"),
                html.P(f"Callback: {callback_name}"),
                html.P(f"Error: {error_msg}"),
                html.Small("LazyString serialization issue resolved with fallback")
            ], className="alert alert-warning")
        except ImportError:
            # Fallback to dictionary
            return {
                "error": True,
                "callback": callback_name,
                "message": error_msg,
                "type": "LazyString_serialization_error"
            }
    
    def test_functionality(self) -> Dict[str, bool]:
        """
        Test plugin functionality
        
        Returns:
            Dictionary with test results
        """
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
    
    @contextmanager
    def temporary_activation(self, **config_overrides):
        """
        Context manager for temporary plugin activation
        
        Args:
            **config_overrides: Configuration options
        """
        was_active = self.is_active
        try:
            if not was_active:
                self.activate(**config_overrides)
            yield self
        finally:
            if not was_active and self.is_active:
                self.deactivate()


# Global plugin instance
lazystring_plugin = LazyStringSerializationPlugin()


def apply_lazystring_fixes(**config_overrides) -> bool:
    """
    Convenience function to apply LazyString fixes
    
    Args:
        **config_overrides: Configuration options
        
    Returns:
        bool: True if fixes applied successfully
    """
    return lazystring_plugin.activate(**config_overrides)


def remove_lazystring_fixes() -> bool:
    """
    Convenience function to remove LazyString fixes
    
    Returns:
        bool: True if fixes removed successfully
    """
    return lazystring_plugin.deactivate()


def lazystring_safe(func: Callable) -> Callable:
    """
    Decorator to make functions safe from LazyString serialization errors
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    return lazystring_plugin.safe_callback(func)


def sanitize_for_json(data: Any) -> Any:
    """
    Convenience function to sanitize data for JSON serialization
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data
    """
    return lazystring_plugin.sanitize_data(data)


if __name__ == "__main__":
    # Test the plugin when run directly
    print("🧪 Testing LazyString Serialization Plugin...")
    
    # Activate plugin
    success = apply_lazystring_fixes(debug_mode=True)
    print(f"Plugin activation: {'✅ Success' if success else '❌ Failed'}")
    
    # Run tests
    test_results = lazystring_plugin.test_functionality()
    print("\nTest Results:")
    for test_name, result in test_results.items():
        status = "✅ Pass" if result else "❌ Fail"
        print(f"  {test_name}: {status}")
    
    # Show usage example
    print("\n📖 Usage Examples:")
    print("1. Apply fixes: apply_lazystring_fixes()")
    print("2. Decorator: @lazystring_safe")
    print("3. Manual sanitization: sanitize_for_json(data)")
    print("4. Temporary use: with lazystring_plugin.temporary_activation():")