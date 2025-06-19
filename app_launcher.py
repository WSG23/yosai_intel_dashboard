#!/usr/bin/env python3
"""
Flask Application Launcher with LazyString Plugin Integration
Resolves TypeError: Type is not JSON serializable: LazyString

This launcher:
1. Applies LazyString fixes BEFORE importing your app
2. Provides plugin-based isolation for easy testing
3. Includes comprehensive error handling
4. Allows easy reversion to original app
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from typing import Optional

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import the LazyString plugin (save the previous plugin code as lazystring_plugin.py)
try:
    from lazystring_test_suite import LazyStringSerializationPlugin, apply_lazystring_fixes
except ImportError:
    print("❌ Error: lazystring_plugin.py not found. Please save the plugin code first.")
    sys.exit(1)


class AppLauncher:
    """
    Application launcher with LazyString error protection
    """
    
    def __init__(self, debug: bool = True):
        self.debug = debug
        self.logger = self._setup_logging()
        self.lazystring_plugin = LazyStringSerializationPlugin(self.logger)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _setup_environment(self) -> None:
        """Setup environment variables"""
        try:
            # Load environment file if it exists
            from dotenv import load_dotenv
            env_file = Path(".env")
            if env_file.exists():
                load_dotenv(env_file, override=True)
                self.logger.info(f"✅ Loaded environment from {env_file}")
        except ImportError:
            self.logger.info("⚠️ python-dotenv not available, skipping .env file")
        
        # Set default environment variables
        defaults = {
            "FLASK_ENV": "development",
            "FLASK_DEBUG": "1" if self.debug else "0",
            "DB_HOST": "localhost",
            "SECRET_KEY": "dev-secret-key-change-in-production",
            "YOSAI_ENV": "development"
        }
        
        for key, value in defaults.items():
            if key not in os.environ:
                os.environ[key] = value
                self.logger.debug(f"Set default {key}={value}")
    
    def _apply_lazystring_protection(self) -> bool:
        """Apply LazyString protection before app import"""
        try:
            self.logger.info("🔧 Applying LazyString protection...")
            
            # Configure plugin for your specific needs
            config = {
                'auto_patch_babel': True,
                'auto_patch_json': True,
                'force_string_conversion': True,
                'fallback_to_repr': True,
                'debug_mode': self.debug
            }
            
            success = self.lazystring_plugin.activate(**config)
            
            if success:
                self.logger.info("✅ LazyString protection activated")
                
                # Run plugin tests
                test_results = self.lazystring_plugin.test_functionality()
                failed_tests = [name for name, result in test_results.items() if not result]
                
                if failed_tests:
                    self.logger.warning(f"⚠️ Some tests failed: {failed_tests}")
                else:
                    self.logger.info("✅ All LazyString protection tests passed")
                    
                return True
            else:
                self.logger.error("❌ LazyString protection activation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error applying LazyString protection: {e}")
            return False
    
    def _create_app(self):
        """Create the Flask application with error handling"""
        try:
            self.logger.info("🏗️ Creating Flask application...")
            
            # Import your app factory
            from core.app_factory import create_application
            
            # Create app with LazyString protection already active
            app = create_application()
            
            if app is None:
                raise RuntimeError("App factory returned None")
            
            self.logger.info("✅ Flask application created successfully")
            return app
            
        except ImportError as e:
            self.logger.error(f"❌ Cannot import app factory: {e}")
            self.logger.error("Make sure core/app_factory.py exists and is accessible")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error creating application: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _wrap_app_callbacks(self, app):
        """Wrap app callbacks with LazyString protection"""
        try:
            # If this is a Dash app, wrap callbacks
            if hasattr(app, 'callback_map'):
                self.logger.info("🔄 Wrapping Dash callbacks with LazyString protection...")
                
                original_callbacks = {}
                for callback_id, callback in app.callback_map.items():
                    if hasattr(callback, 'function'):
                        original_callbacks[callback_id] = callback.function
                        callback.function = self.lazystring_plugin.safe_callback(callback.function)
                
                self.logger.info(f"✅ Wrapped {len(original_callbacks)} callbacks")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not wrap callbacks: {e}")
    
    def launch(self, host: str = "127.0.0.1", port: int = 8050) -> Optional[int]:
        """
        Launch the application with LazyString protection
        
        Args:
            host: Host to bind to
            port: Port to bind to
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            print("🚀 Flask Application Launcher with LazyString Protection")
            print("=" * 60)
            
            # Setup environment
            self._setup_environment()
            
            # Apply LazyString protection BEFORE importing app
            if not self._apply_lazystring_protection():
                print("❌ Failed to apply LazyString protection. Exiting.")
                return 1
            
            # Create application
            app = self._create_app()
            if app is None:
                print("❌ Failed to create application. Exiting.")
                return 1
            
            # Wrap callbacks if needed
            self._wrap_app_callbacks(app)
            
            # Launch application
            print(f"\n🌐 Starting server at http://{host}:{port}")
            print("🔧 LazyString errors should be eliminated")
            print("🛑 Press Ctrl+C to stop\n")
            
            # Check if port is available
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.logger.warning(f"⚠️ Port {port} appears to be in use")
                # Try to find an alternative port
                for alt_port in range(port + 1, port + 10):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex((host, alt_port))
                    sock.close()
                    if result != 0:
                        port = alt_port
                        print(f"🔄 Using alternative port {port}")
                        break
            
            # Run the application
            if hasattr(app, 'run_server'):
                # Dash application
                app.run_server(debug=self.debug, host=host, port=port)
            else:
                # Flask application
                app.run(debug=self.debug, host=host, port=port)
            
            return 0
            
        except KeyboardInterrupt:
            print("\n🛑 Application stopped by user")
            return 0
        except Exception as e:
            self.logger.error(f"❌ Application launch failed: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return 1
        finally:
            # Cleanup
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self.lazystring_plugin.is_active:
                self.logger.info("🧹 Cleaning up LazyString plugin...")
                self.lazystring_plugin.deactivate()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class OriginalAppLauncher:
    """
    Launcher for the original app without LazyString fixes
    Use this to test if your original app works without modifications
    """
    
    def __init__(self, debug: bool = True):
        self.debug = debug
        self.logger = logging.getLogger(__name__)
    
    def launch(self, host: str = "127.0.0.1", port: int = 8051) -> Optional[int]:
        """Launch original app without LazyString protection"""
        try:
            print("🔄 Original Application Launcher (No LazyString Protection)")
            print("=" * 65)
            print("⚠️  WARNING: This may fail with LazyString serialization errors")
            print()
            
            # Load environment
            try:
                from dotenv import load_dotenv
                if Path(".env").exists():
                    load_dotenv(override=True)
            except ImportError:
                pass
            
            # Import and create app WITHOUT LazyString protection
            from core.app_factory import create_application
            app = create_application()
            
            if app is None:
                raise RuntimeError("App factory returned None")
            
            print(f"🌐 Starting original app at http://{host}:{port}")
            print("🔍 If you see LazyString errors, use the protected launcher instead\n")
            
            if hasattr(app, 'run_server'):
                app.run_server(debug=self.debug, host=host, port=port)
            else:
                app.run(debug=self.debug, host=host, port=port)
            
            return 0
            
        except Exception as e:
            print(f"❌ Original app failed: {e}")
            print(f"This confirms you need LazyString protection")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Flask App Launcher with LazyString Protection")
    parser.add_argument("--mode", choices=["protected", "original"], default="protected",
                       help="Launch mode: protected (with LazyString fixes) or original")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8050, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", default=True, help="Enable debug mode")
    parser.add_argument("--production", action="store_true", help="Run in production mode")
    
    args = parser.parse_args()
    
    # Override debug mode for production
    if args.production:
        args.debug = False
        os.environ["FLASK_ENV"] = "production"
        os.environ["FLASK_DEBUG"] = "0"
    
    if args.mode == "protected":
        launcher = AppLauncher(debug=args.debug)
        return launcher.launch(host=args.host, port=args.port)
    else:
        launcher = OriginalAppLauncher(debug=args.debug)
        return launcher.launch(host=args.host, port=args.port)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)