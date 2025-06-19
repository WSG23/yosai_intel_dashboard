#!/usr/bin/env python3
"""
Corrected app.py with LazyString Fix
Using the correct import: create_application from core.app_factory
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the correct create_application function
from core.app_factory import create_application
from config.yaml_config import ConfigurationManager

# Import LazyString fix plugin
from plugins.builtin.lazystring_fix_plugin import (
    initialize_lazystring_fix, 
    LazyStringFixConfig
)


def main():
    """Main application entry point with LazyString fix"""
    try:
        # Get configuration path
        config_path = get_config_path()
        
        # Load configuration
        config_manager = ConfigurationManager()
        config_manager.load_configuration(config_path)
        config_manager.print_startup_info()
        
        # Create the Dash application
        logger.info("Creating Yosai Intel Dashboard...")
        app = create_application()  # <-- Correct function call
        
        if app is None:
            print("❌ Failed to create dashboard application")
            sys.exit(1)
        
        # Apply LazyString fix with full configuration
        logger.info("Applying LazyString fix plugin...")
        
        # Configure based on environment
        is_production = os.getenv("YOSAI_ENV", "development").lower() in ["production", "prod"]
        
        lazystring_config = LazyStringFixConfig(
            enabled=True,
            auto_wrap_callbacks=True,    # Automatically wrap all callbacks
            deep_sanitize=True,          # Handle nested objects
            log_conversions=not is_production,  # Log only in development
            fallback_locale="en"         # Default locale
        )
        
        # Initialize the plugin
        try:
            plugin = initialize_lazystring_fix(app, lazystring_config)
            logger.info("✅ LazyString fix plugin initialized successfully")
            
            # Log statistics
            stats = plugin.get_stats()
            logger.info(f"LazyString plugin stats: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LazyString fix: {e}")
            # Continue anyway - app might still work for non-i18n parts
        
        # Apply CSRF workaround to the Flask server
        app.server.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY"))
        app.server.config["WTF_CSRF_ENABLED"] = False
        
        # Configure logging level from configuration
        app_config = config_manager.app_config
        logging.getLogger().setLevel(getattr(logging, app_config.log_level.upper()))
        
        # Run the application
        app.run(debug=app_config.debug, host=app_config.host, port=app_config.port)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)


def get_config_path() -> Optional[str]:
    """Select the configuration file based on environment variables."""
    from core.secret_manager import SecretManager
    
    manager = SecretManager()
    try:
        config_file = manager.get("YOSAI_CONFIG_FILE")
    except KeyError:
        config_file = None
        
    if config_file and Path(config_file).exists():
        print(f"📋 Using config file from YOSAI_CONFIG_FILE: {config_file}")
        return config_file
    
    env = manager.get("YOSAI_ENV", "development").lower()
    env_config_map = {
        "production": "config/production.yaml",
        "prod": "config/production.yaml",
        "test": "config/test.yaml",
        "testing": "config/test.yaml",
        "development": "config/config.yaml",
        "dev": "config/config.yaml",
    }
    
    config_path = env_config_map.get(env, "config/config.yaml")
    if Path(config_path).exists():
        print(f"📋 Using environment config: {config_path} (YOSAI_ENV={env})")
        return config_path
        
    print(f"⚠️  Config file not found: {config_path}, using defaults")
    return None


# For WSGI deployment
def get_app() -> Optional[Any]:
    """Get the Dash app instance for WSGI servers"""
    try:
        # Create app
        app = create_application()
        
        if app is not None:
            # Apply LazyString fix for production
            lazystring_config = LazyStringFixConfig(
                enabled=True,
                auto_wrap_callbacks=True,
                deep_sanitize=True,
                log_conversions=False,  # No logging in production
                fallback_locale="en"
            )
            initialize_lazystring_fix(app, lazystring_config)
            
        return app
    except Exception as e:
        logger.error(f"Error creating WSGI app: {e}")
        return None


# WSGI app instance
app = get_app()
server = app.server if app is not None else None

# Module execution
if __name__ == "__main__":
    main()