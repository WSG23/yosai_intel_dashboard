"""Service locator pattern for configuration components"""

import logging
from typing import Optional, Dict, Any, TypeVar, Type
from .interfaces import IDatabaseManager, ICacheManager, IConfigurationManager
from .factories import DatabaseManagerFactory, CacheManagerFactory

logger = logging.getLogger(__name__)
T = TypeVar('T')

class ConfigurationServiceLocator:
    """Service locator for configuration components"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}

    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service instance"""
        self._services[service_name] = service_instance
        logger.info(f"Registered service: {service_name}")

    def register_singleton(self, service_name: str, factory_func: callable) -> None:
        """Register a singleton service factory"""
        self._singletons[service_name] = factory_func
        logger.info(f"Registered singleton factory: {service_name}")

    def get_service(self, service_name: str) -> Optional[Any]:
        """Get service by name"""
        # Check direct services first
        if service_name in self._services:
            return self._services[service_name]

        # Check singleton factories
        if service_name in self._singletons:
            if f"_{service_name}_instance" not in self._services:
                factory = self._singletons[service_name]
                instance = factory()
                self._services[f"_{service_name}_instance"] = instance
                return instance
            return self._services[f"_{service_name}_instance"]

        logger.warning(f"Service not found: {service_name}")
        return None

    def get_database_manager(self) -> Optional[IDatabaseManager]:
        """Get database manager service"""
        return self.get_service('database_manager')

    def get_cache_manager(self) -> Optional[ICacheManager]:
        """Get cache manager service"""
        return self.get_service('cache_manager')

    def get_configuration_manager(self) -> Optional[IConfigurationManager]:
        """Get configuration manager service"""
        return self.get_service('configuration_manager')

    def initialize_from_config(self, config_manager: IConfigurationManager) -> None:
        """Initialize all services from configuration"""
        # Create database manager
        db_manager = DatabaseManagerFactory.create_manager(
            config_manager.get_database_config()
        )
        self.register_service('database_manager', db_manager)

        # Create cache manager
        cache_manager = CacheManagerFactory.create_manager(
            config_manager.get_cache_config()
        )
        self.register_service('cache_manager', cache_manager)

        # Register configuration manager
        self.register_service('configuration_manager', config_manager)

        logger.info("Configuration services initialized")

    def start_services(self) -> None:
        """Start all lifecycle-aware services"""
        cache_manager = self.get_cache_manager()
        if cache_manager:
            cache_manager.start()

        logger.info("Configuration services started")

    def stop_services(self) -> None:
        """Stop all lifecycle-aware services"""
        cache_manager = self.get_cache_manager()
        if cache_manager:
            cache_manager.stop()

        db_manager = self.get_database_manager()
        if db_manager:
            db_manager.close_connection()

        logger.info("Configuration services stopped")

# Global service locator instance
_service_locator = ConfigurationServiceLocator()

def get_service_locator() -> ConfigurationServiceLocator:
    """Get global service locator instance"""
    return _service_locator
