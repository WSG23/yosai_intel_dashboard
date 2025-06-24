#!/usr/bin/env python3
"""
Streamlined Main Application
Uses simplified configuration and component systems
"""
import logging
import os
from config.config import get_config
from core.app_factory import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_startup_info():
    """Print application startup information"""
    config = get_config()
    app_config = config.get_app_config()
    
    print("\n" + "=" * 60)
    print("🏯 YŌSAI INTEL DASHBOARD")
    print("=" * 60)
    print(f"🌐 URL: http://{app_config.host}:{app_config.port}")
    print(f"🔧 Debug Mode: {app_config.debug}")
    print(f"🌍 Environment: {config.config.environment}")
    print("📊 Analytics: http://{app_config.host}:{app_config.port}/analytics")
    print("📁 Upload: http://{app_config.host}:{app_config.port}/upload")
    print("=" * 60)
    
    if app_config.debug:
        print("⚠️  Running in DEBUG mode - do not use in production!")
    
    print("\n🚀 Dashboard starting...")


def main():
    """Main application entry point"""
    try:
        # Load configuration
        config = get_config()
        app_config = config.get_app_config()
        
        # Print startup information
        print_startup_info()
        
        # Create the Dash application
        app = create_app()
        
        logger.info("✅ Application created successfully")
        
        # Run the application
        app.run_server(
            debug=app_config.debug,
            host=app_config.host,
            port=app_config.port
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()
