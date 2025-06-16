# app.py - SIMPLIFIED VERSION (replace your current app.py)
"""
Yōsai Intel Dashboard - Main Application Entry Point
"""

import sys
import logging
from typing import Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Main application entry point"""
    try:
        # Import core modules
        from core.config_manager import ConfigManager
        from core.app_factory import create_application
        
        # Create configuration
        config_manager = ConfigManager.from_environment()
        
        # Print startup info
        config_manager.print_startup_info()
        
        # Create application
        app = create_application()
        
        if app is None:
            print("❌ Failed to create dashboard application")
            sys.exit(1)
        
        # Run application
        app.run(
            debug=config_manager.app_config.debug,
            host=config_manager.app_config.host,
            port=config_manager.app_config.port
        )
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)

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