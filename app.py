# app.py - UPDATED: Now uses YAML Configuration System
"""
Yōsai Intel Dashboard - Main Application Entry Point
UPDATED: Now supports YAML configuration with environment overrides
"""

import sys
import logging
import os
from typing import Optional, Any
from pathlib import Path

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Main application entry point with YAML configuration"""
    try:
        # Import core modules with YAML config support
        from core.app_factory import create_application
        from config.yaml_config import ConfigurationManager
        
        # Determine configuration file based on environment
        config_path = get_config_path()
        
        # Create and load configuration
        config_manager = ConfigurationManager()
        config_manager.load_configuration(config_path)
        
        # Print startup info
        config_manager.print_startup_info()
        
        # Create application with configuration
        app = create_application()
        
        if app is None:
            print("❌ Failed to create dashboard application")
            sys.exit(1)
        
        # Get app configuration
        app_config = config_manager.app_config
        
        # Configure logging level from config
        logging.getLogger().setLevel(getattr(logging, app_config.log_level.upper()))
        
        # Run application
        app.run(
            debug=app_config.debug,
            host=app_config.host,
            port=app_config.port
        )
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)

def get_config_path() -> Optional[str]:
    """Determine which configuration file to use based on environment"""
    
    # Check for explicit config file in environment
    config_file = os.getenv('YOSAI_CONFIG_FILE')
    if config_file and Path(config_file).exists():
        print(f"📋 Using config file from YOSAI_CONFIG_FILE: {config_file}")
        return config_file
    
    # Check for environment-specific config
    env = os.getenv('YOSAI_ENV', 'development').lower()
    
    env_config_map = {
        'production': 'config/production.yaml',
        'prod': 'config/production.yaml',
        'test': 'config/test.yaml',
        'testing': 'config/test.yaml',
        'development': 'config/config.yaml',
        'dev': 'config/config.yaml'
    }
    
    config_path = env_config_map.get(env, 'config/config.yaml')
    
    if Path(config_path).exists():
        print(f"📋 Using environment config: {config_path} (YOSAI_ENV={env})")
        return config_path
    else:
        print(f"⚠️  Config file not found: {config_path}, using defaults")
        return None

# For WSGI deployment
def get_app() -> Optional[Any]:
    """Get the Dash app instance for WSGI servers"""
    try:
        from core.app_factory import create_application
        return create_application()
    except Exception as e:
        logger.error(f"Error creating WSGI app: {e}")
        return None

# WSGI app instance
app = get_app()
server = app.server if app is not None else None

# Module execution
if __name__ == '__main__':
    main()
