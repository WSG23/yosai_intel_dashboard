"""Simplified dependency injection container"""
from typing import Dict, Any, TypeVar, Type, Callable, Optional
from functools import lru_cache
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)


class Container:
    """Simple dependency injection container"""

    def __init__(self):
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._instances: Dict[str, Any] = {}

    def register_factory(self, name: str, factory: Callable[[], T]) -> None:
        """Register a factory function"""
        self._factories[name] = factory
        logger.debug(f"Registered factory: {name}")

    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """Register a singleton factory"""
        self._singletons[name] = factory
        logger.debug(f"Registered singleton: {name}")

    def register_instance(self, name: str, instance: T) -> None:
        """Register a pre-created instance"""
        self._instances[name] = instance
        logger.debug(f"Registered instance: {name}")

    def get(self, name: str) -> Any:
        """Get service by name"""
        # Check instances first (highest priority)
        if name in self._instances:
            return self._instances[name]

        # Check singletons
        if name in self._singletons:
            if name not in self._instances:
                self._instances[name] = self._singletons[name]()
                logger.debug(f"Created singleton instance: {name}")
            return self._instances[name]

        # Check factories
        if name in self._factories:
            instance = self._factories[name]()
            logger.debug(f"Created factory instance: {name}")
            return instance

        raise KeyError(f"Service '{name}' not registered")

    def get_typed(self, service_type: Type[T], name: Optional[str] = None) -> T:
        """Get service with type hint"""
        service_name = name or service_type.__name__.lower()
        return self.get(service_name)

    def clear(self) -> None:
        """Clear all registrations (useful for testing)"""
        self._factories.clear()
        self._singletons.clear()
        self._instances.clear()
        logger.debug("Container cleared")


# Service registration helper functions
def setup_container() -> 'Container':
    """Setup container with default services"""
    from config.config_manager import get_config
    from database.connection import create_database_manager
    from services.analytics import create_analytics_service

    container = Container()

    # Register configuration
    config = get_config()
    container.register_instance('config', config)

    # Register database manager as singleton
    container.register_singleton(
        'database_manager',
        lambda: create_database_manager(config.database)
    )

    # Register database connection as singleton
    container.register_singleton(
        'database_connection',
        lambda: container.get('database_manager').get_connection()
    )

    # Register analytics service as singleton
    container.register_singleton(
        'analytics_service',
        lambda: create_analytics_service(container.get('database_connection'))
    )

    logger.info("Container setup complete")
    return container


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get global container instance"""
    global _container
    if _container is None:
        _container = setup_container()
    return _container


def get_service(name: str) -> Any:
    """Get service from global container"""
    return get_container().get(name)


def get_typed_service(service_type: Type[T], name: Optional[str] = None) -> T:
    """Get typed service from global container"""
    return get_container().get_typed(service_type, name)


# Context manager for testing
class TestContainer:
    """Test container context manager"""

    def __init__(self):
        self.original_container = None
        self.test_container = Container()

    def __enter__(self) -> 'Container':
        global _container
        self.original_container = _container
        _container = self.test_container
        return self.test_container

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _container
        _container = self.original_container
