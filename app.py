#!/usr/bin/env python3
"""
Main application entry point
"""
import logging
import os
from core.app_factory import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Create the Dash application
        app = create_app()
        
        # Get configuration from environment
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', '8050'))
        
        logger.info(f"Starting application on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Run the application
        app.run_server(
            debug=debug,
            host=host,
            port=port
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main()
