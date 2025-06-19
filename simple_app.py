#!/usr/bin/env python3
"""
Simplified app.py with LazyString Fix Plugin
Copy this template and modify as needed
"""

import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import your app factory
from core.app_factory import core.app_factory_json_safe

# Import LazyString fix plugin
from plugins.builtin.lazystring_fix_plugin import (
    initialize_lazystring_fix, 
    LazyStringFixConfig
)


# Create the app
logger.info("Creating Yosai Intel Dashboard...")
app = YosaiApplicationFactory.create_application()

if app is not None:
    # Apply LazyString fix with full configuration
    config = LazyStringFixConfig(
        enabled=True,                    # Enable the plugin
        auto_wrap_callbacks=True,        # Automatically wrap all callbacks
        deep_sanitize=True,              # Handle nested objects
        log_conversions=True,            # Set False for production
        fallback_locale="en"             # Default locale
    )
    
    # Initialize the plugin - THIS IS THE KEY LINE
    plugin = initialize_lazystring_fix(app, config)
    logger.info("✅ LazyString fix applied")
    
    # Optional: Print statistics
    stats = plugin.get_stats()
    logger.info(f"Plugin stats: {stats}")
else:
    logger.error("Failed to create app")
    exit(1)


# Run the app
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    port = int(os.getenv("PORT", "8050"))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"Starting server on {host}:{port}")
    
    app.run_server(
        debug=debug,
        host=host,
        port=port,
        dev_tools_hot_reload=debug
    )

# For production deployment
server = app.server