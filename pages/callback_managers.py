"""
Simplified callback managers
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

class AnalyticsCallbackManager:
    """Callback manager for analytics page"""
    
    def __init__(self, callback_registry, container=None):
        self.registry = callback_registry
        self.container = container
        
    def register_all(self):
        """Register analytics page callbacks"""
        try:
            from pages import register_page_callbacks
            success = register_page_callbacks('deep_analytics', None, self.container)
            if success:
                logger.info("Analytics callbacks registered")
            else:
                logger.warning("Analytics callbacks registration failed")
        except Exception as e:
            logger.error(f"Error registering analytics callbacks: {e}")

# FileUploadPageCallbackManager removed - not needed anymore