"""
Page-specific callback managers
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

            # Use existing page callback registration for now
            # TODO: Migrate to centralized registry in future
            logger.info("Analytics callbacks registered through legacy system")

        except Exception as e:
            logger.error(f"Error registering analytics callbacks: {e}")


class FileUploadCallbackManager:
    """Callback manager for file upload page"""

    def __init__(self, callback_registry, container=None):
        self.registry = callback_registry
        self.container = container

    def register_all(self):
        """Register file upload page callbacks"""
        try:
            from pages import register_page_callbacks

            # Use existing page callback registration for now
            # TODO: Migrate to centralized registry in future
            logger.info("File upload callbacks registered through legacy system")

        except Exception as e:
            logger.error(f"Error registering file upload callbacks: {e}")
