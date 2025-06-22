"""
Page-specific callback managers - Updated to work with existing callbacks
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
            register_page_callbacks('deep_analytics', None, self.container)
            logger.info("Analytics callbacks registered")
        except Exception as e:
            logger.error(f"Error registering analytics callbacks: {e}")


