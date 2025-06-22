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


class FileUploadPageCallbackManager:
    """Callback manager for file upload workflow - now uses existing callbacks"""
    
    def __init__(self, callback_registry, container=None):
        self.registry = callback_registry
        self.container = container
        
    def register_all(self):
        """Register file upload callbacks - the @callback decorators in file_uploader.py handle this"""
        try:
            # The callbacks are already registered via @callback decorators
            # in components/analytics/file_uploader.py
            # Just log that they should be working
            logger.info("File upload callbacks handled by @callback decorators in file_uploader.py")
            
        except Exception as e:
            logger.error(f"Error with file upload callbacks: {e}")
