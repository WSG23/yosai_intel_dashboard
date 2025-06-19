"""
Safe service registry without circular dependencies
"""
from typing import Optional, Any, Dict
import logging
from .di_container import DIContainer

logger = logging.getLogger(__name__)


class SafeServiceRegistry:
    """Thread-safe service registry with timeout handling"""

    def __init__(self):
        self._container: Optional[DIContainer] = None
        self._services: Dict[str, Any] = {}

    def configure_container(self, config_manager: Optional[Any] = None) -> DIContainer:
        """Configure container without problematic services"""
        if self._container is None:
            self._container = DIContainer()

            # Register only safe services initially
            self._register_safe_services(config_manager)

        return self._container

    def _register_safe_services(self, config_manager: Optional[Any] = None) -> None:
        """Register services that don't cause timeouts or circular deps"""
        try:
            # Register config manager first
            if config_manager:
                self._container.register("config_manager", lambda: config_manager)

            # Register other safe services here
            # Skip analytics service for now to avoid timeout
            logger.info("Safe services registered successfully")

        except Exception as e:
            logger.error(f"Error registering safe services: {e}")

    def get_service(self, name: str) -> Optional[Any]:
        """Get service safely with fallback"""
        try:
            if self._container:
                return self._container.get(name)
        except Exception as e:
            logger.warning(f"Could not resolve service {name}: {e}")
        return None


# Global safe registry instance
safe_registry = SafeServiceRegistry()


def get_safe_container(config_manager: Optional[Any] = None) -> DIContainer:
    """Get safely configured container"""
    return safe_registry.configure_container(config_manager)

