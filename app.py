#!/usr/bin/env python3
"""
Fixed Main Application - No import issues
"""
import logging
import os
import sys

# Configure logging first
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize global device learning service
from services.device_learning_service import DeviceLearningService

learning_service = DeviceLearningService()


def print_startup_info(app_config):
    """Print application startup information"""
    print("\n" + "=" * 60)
    print("🏯 YŌSAI INTEL DASHBOARD")
    print("=" * 60)
    print(f"🌐 URL: http://{app_config.host}:{app_config.port}")
    print(f"🔧 Debug Mode: {app_config.debug}")
    print(f"🌍 Environment: {app_config.environment}")
    print(f"📊 Analytics: http://{app_config.host}:{app_config.port}/analytics")
    print(f"📁 Upload: http://{app_config.host}:{app_config.port}/upload")
    print("=" * 60)

    if app_config.debug:
        print("⚠️  Running in DEBUG mode - do not use in production!")

    print("\n🚀 Dashboard starting...")


def main():
    """Main application entry point"""
    try:
        # Import configuration
        try:
            from config.config import get_config

            config = get_config()
            app_config = config.get_app_config()
            logger.info("✅ Configuration loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            print(f"\n❌ Configuration Error: {e}")
            print("💡 Make sure config/config.py exists and is properly formatted")
            sys.exit(1)

        # Print startup information
        print_startup_info(app_config)

        # Import and create the Dash application
        try:
            from core.app_factory import create_app

            app = create_app()
            logger.info("✅ Application created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create application: {e}")
            print(f"\n❌ Application Creation Error: {e}")
            print(
                "💡 Make sure core/app_factory.py exists and dependencies are installed"
            )
            sys.exit(1)

        # Run the application
        try:
            app.run_server(
                debug=app_config.debug, host=app_config.host, port=app_config.port
            )
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user")
        except Exception as e:
            logger.error(f"❌ Application runtime error: {e}")
            print(f"\n❌ Runtime Error: {e}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print(f"\n❌ Unexpected Error: {e}")
        print("💡 Check logs for more details")
        sys.exit(1)


if __name__ == "__main__":
    main()
