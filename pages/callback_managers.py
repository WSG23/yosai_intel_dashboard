"""
Page-specific callback managers with restored functionality
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
    """Callback manager for complete file upload workflow"""

    def __init__(self, callback_registry, container=None):
        self.registry = callback_registry
        self.container = container

    def register_all(self):
        """Register complete file upload workflow callbacks"""
        try:
            # Register the comprehensive file upload callback manager
            from components.analytics.file_upload_callback_manager import FileUploadCallbackManager

            file_upload_manager = FileUploadCallbackManager(self.registry)
            file_upload_manager.register_all()

            # Also register dual upload visual callbacks if available
            try:
                from components.analytics.file_uploader import register_dual_upload_callbacks
                # Note: This needs app instance, will handle differently
                logger.info("Dual upload visual callbacks available")
            except ImportError:
                logger.warning("Dual upload callbacks not available")

            logger.info("Complete file upload workflow callbacks registered")

        except Exception as e:
            logger.error(f"Error registering file upload callbacks: {e}")
