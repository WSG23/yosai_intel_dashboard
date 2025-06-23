"""
Simplified service container for dependency injection
"""
from typing import Dict, Any, Type, Callable, Optional, TypeVar
import logging

T = TypeVar('T')

class ServiceContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_instance(self, name: str, instance: Any) -> None:
        """Register existing service instance"""
        self._services[name] = instance
        self.logger.debug(f"Registered instance: {name}")
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register factory function for transient services"""
        self._factories[name] = factory
        self.logger.debug(f"Registered factory: {name}")
    
    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """Register singleton factory"""
        self._factories[name] = factory
        self._singletons[name] = None
        self.logger.debug(f"Registered singleton: {name}")
    
    def get(self, name: str) -> Any:
        """Get service by name"""
        # Check direct instances first
        if name in self._services:
            return self._services[name]
        
        # Check singletons
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            return self._factories[name]()
        
        raise KeyError(f"Service '{name}' not registered")
    
    def has(self, name: str) -> bool:
        """Check if service is registered"""
        return (name in self._services or 
                name in self._factories or 
                name in self._singletons)
    
    def reset_singletons(self) -> None:
        """Reset all singletons (useful for testing)"""
        for name in self._singletons:
            self._singletons[name] = None

# Global container instance
_container: Optional[ServiceContainer] = None

def get_container() -> ServiceContainer:
    """Get or create global container"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container

def configure_services() -> None:
    """Configure all application services"""
    container = get_container()
    
    # Register database
    from config.database_manager import DatabaseManager
    container.register_singleton('database', DatabaseManager.from_environment)
    
    # Register analytics service
    from services.analytics_service import create_analytics_service
    container.register_singleton('analytics_service', 
                                lambda: create_analytics_service(container.get('database')))
    
    # Register file processor
    from services.file_processor_service import FileProcessorService
    container.register_factory('file_processor', FileProcessorService)
    
    logging.info("✅ Services configured successfully")

# Module exports
__all__ = ['ServiceContainer', 'get_container', 'configure_services']
