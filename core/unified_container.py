from typing import Dict, Any, Callable, TypeVar, Optional
import logging
from abc import ABC, abstractmethod

T = TypeVar('T')

class ServiceLifetime:
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class ServiceDescriptor:
    def __init__(self, name: str, factory: Callable[[], Any], lifetime: str):
        self.name = name
        self.factory = factory
        self.lifetime = lifetime

class IServiceContainer(ABC):
    @abstractmethod
    def register(self, name: str, factory: Callable[[], T], lifetime: str = ServiceLifetime.TRANSIENT) -> None:
        pass

    @abstractmethod
    def get(self, name: str) -> Any:
        pass

class UnifiedServiceContainer(IServiceContainer):
    """Single, unified dependency injection container"""

    def __init__(self):
        self._services: Dict[str, ServiceDescriptor] = {}
        self._singletons: Dict[str, Any] = {}
        self._scoped: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, name: str, factory: Callable[[], T], lifetime: str = ServiceLifetime.TRANSIENT) -> None:
        """Register a service with specified lifetime"""
        descriptor = ServiceDescriptor(name, factory, lifetime)
        self._services[name] = descriptor
        self.logger.debug(f"Registered {lifetime} service: {name}")

    def register_singleton(self, name: str, factory: Callable[[], T]) -> None:
        """Convenience method for singleton registration"""
        self.register(name, factory, ServiceLifetime.SINGLETON)

    def register_instance(self, name: str, instance: T) -> None:
        """Register existing instance as singleton"""
        self._singletons[name] = instance
        self.register(name, lambda: instance, ServiceLifetime.SINGLETON)

    def get(self, name: str) -> Any:
        """Get service instance"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")

        descriptor = self._services[name]

        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if name not in self._singletons:
                self._singletons[name] = descriptor.factory()
            return self._singletons[name]
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            # For now, treat scoped like singleton
            if name not in self._scoped:
                self._scoped[name] = descriptor.factory()
            return self._scoped[name]
        else:  # TRANSIENT
            return descriptor.factory()

    def clear_scope(self) -> None:
        """Clear scoped services (useful for request boundaries)"""
        self._scoped.clear()

    def reset(self) -> None:
        """Reset all services (useful for testing)"""
        self._singletons.clear()
        self._scoped.clear()

# Global container instance
_container: Optional[UnifiedServiceContainer] = None


def get_container() -> UnifiedServiceContainer:
    """Get global container instance"""
    global _container
    if _container is None:
        _container = UnifiedServiceContainer()
    return _container


def reset_container() -> None:
    """Reset global container (for testing)"""
    global _container
    _container = None
