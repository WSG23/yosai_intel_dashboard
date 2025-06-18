#!/usr/bin/env python3
"""
Debug JSON Serialization Error
Pinpoints exactly which callback is returning function objects
"""

import sys
import traceback
import json
import functools
from typing import Any, Callable
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CallbackDebugger:
    """Debug callback functions to find JSON serialization issues"""
    
    def __init__(self):
        self.callback_results = {}
        self.problematic_callbacks = []
    
    def debug_callback_output(self, callback_name: str, output: Any) -> Any:
        """Debug a callback's output for JSON serialization issues"""
        try:
            # Test JSON serialization
            json.dumps(output)
            print(f"✅ {callback_name}: JSON serializable")
            self.callback_results[callback_name] = {"status": "ok", "type": type(output).__name__}
            return output
        except (TypeError, ValueError) as e:
            print(f"❌ {callback_name}: JSON error - {e}")
            
            # Analyze what's causing the issue
            issue_detail = self._analyze_output_issue(output)
            self.callback_results[callback_name] = {
                "status": "error",
                "error": str(e),
                "analysis": issue_detail
            }
            self.problematic_callbacks.append(callback_name)
            
            # Return a safe fallback
            return self._create_safe_fallback(callback_name, output, str(e))
    
    def _analyze_output_issue(self, output: Any) -> str:
        """Analyze what's causing the JSON serialization issue"""
        if callable(output):
            return f"Function object: {getattr(output, '__name__', 'anonymous')}"
        
        if isinstance(output, (list, tuple)):
            for i, item in enumerate(output):
                if callable(item):
                    return f"Function in position {i}: {getattr(item, '__name__', 'anonymous')}"
                try:
                    json.dumps(item)
                except (TypeError, ValueError):
                    return f"Non-serializable item at position {i}: {type(item).__name__}"
        
        if isinstance(output, dict):
            for key, value in output.items():
                if callable(value):
                    return f"Function at key '{key}': {getattr(value, '__name__', 'anonymous')}"
                try:
                    json.dumps(value)
                except (TypeError, ValueError):
                    return f"Non-serializable value at key '{key}': {type(value).__name__}"
        
        if hasattr(output, '__dict__'):
            return f"Complex object: {type(output).__name__}"
        
        return f"Unknown issue with type: {type(output).__name__}"
    
    def _create_safe_fallback(self, callback_name: str, original_output: Any, error: str) -> Any:
        """Create a safe fallback for problematic outputs"""
        try:
            from dash import html
            return html.Div([
                html.H4(f"⚠️ Callback Issue: {callback_name}", className="text-warning"),
                html.P(f"Error: {error}"),
                html.P(f"Type: {type(original_output).__name__}"),
                html.Small("This callback returned a non-serializable object")
            ], className="alert alert-warning")
        except ImportError:
            # Ultimate fallback
            return {
                "error": True,
                "callback": callback_name,
                "message": error,
                "type": type(original_output).__name__
            }
    
    def wrap_all_callbacks(self, app):
        """Wrap all callbacks in the app for debugging"""
        if hasattr(app, 'callback_map'):
            original_callbacks = {}
            
            for callback_id, callback_obj in app.callback_map.items():
                callback_name = f"callback_{callback_id}"
                original_func = callback_obj['callback']
                
                # Store original
                original_callbacks[callback_id] = original_func
                
                # Create wrapped version
                @functools.wraps(original_func)
                def debug_wrapper(func=original_func, name=callback_name):
                    def wrapper(*args, **kwargs):
                        try:
                            result = func(*args, **kwargs)
                            return self.debug_callback_output(name, result)
                        except Exception as e:
                            print(f"❌ {name} crashed: {e}")
                            traceback.print_exc()
                            return self._create_safe_fallback(name, None, str(e))
                    return wrapper
                
                # Replace callback
                callback_obj['callback'] = debug_wrapper()
        
        print(f"🔍 Wrapped {len(app.callback_map)} callbacks for debugging")


def patch_dash_for_debugging():
    """Patch Dash to intercept callback registration"""
    try:
        import dash
        
        # Store original callback decorator
        original_callback = dash.Dash.callback
        
        def debug_callback(self, *args, **kwargs):
            """Wrapped callback that adds debugging"""
            def decorator(func):
                callback_name = getattr(func, '__name__', 'anonymous')
                print(f"🔍 Registering callback: {callback_name}")
                
                @functools.wraps(func)
                def debug_wrapper(*cb_args, **cb_kwargs):
                    try:
                        result = func(*cb_args, **cb_kwargs)
                        
                        # Debug the result
                        debugger = CallbackDebugger()
                        safe_result = debugger.debug_callback_output(callback_name, result)
                        return safe_result
                        
                    except Exception as e:
                        print(f"❌ Callback {callback_name} crashed: {e}")
                        traceback.print_exc()
                        
                        try:
                            from dash import html
                            return html.Div([
                                html.H4(f"⚠️ Callback Error: {callback_name}"),
                                html.P(f"Error: {str(e)}"),
                            ], className="alert alert-danger")
                        except ImportError:
                            return {"error": True, "callback": callback_name, "message": str(e)}
                
                # Register the wrapped callback
                return original_callback(self, *args, **kwargs)(debug_wrapper)
            
            return decorator
        
        # Monkey patch Dash
        dash.Dash.callback = debug_callback
        print("✅ Patched Dash for callback debugging")
        
    except Exception as e:
        print(f"❌ Failed to patch Dash: {e}")


def create_debug_app():
    """Create a debug version of your app"""
    # Load environment first
    import os
    from pathlib import Path
    
    try:
        from dotenv import load_dotenv
        if Path(".env").exists():
            load_dotenv(override=True)
            print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not available")
    
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
    
    # Patch Dash for debugging BEFORE importing app
    patch_dash_for_debugging()
    
    try:
        print("🔍 Creating debug version of your app...")
        
        # Import your app factory
        from core.app_factory import create_application
        
        app = create_application()
        if app:
            print("✅ Debug app created successfully")
            print("🔍 All callbacks are now wrapped for debugging")
            print("❌ Any JSON serialization errors will be caught and displayed")
            return app
        else:
            print("❌ Failed to create debug app")
            return None
            
    except Exception as e:
        print(f"❌ Error creating debug app: {e}")
        traceback.print_exc()
        return None


def main():
    """Main debug function"""
    print("🔍 JSON Serialization Error Debugger")
    print("=" * 40)
    print("This will help identify exactly which callback is causing the error")
    print()
    
    app = create_debug_app()
    if app:
        print("\n🚀 Starting debug server...")
        print("🌐 URL: http://127.0.0.1:8052")
        print("🔍 Watch the console for JSON serialization errors")
        print("❌ Any problematic callbacks will be identified and replaced with error messages")
        print()
        
        try:
            app.run(debug=True, host="127.0.0.1", port=8052)
        except KeyboardInterrupt:
            print("\n👋 Debug session stopped")
        except Exception as e:
            print(f"\n❌ Debug server error: {e}")
            traceback.print_exc()
    else:
        print("❌ Could not create debug app")


if __name__ == "__main__":
    main()