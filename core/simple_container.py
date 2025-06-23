"""
Simplified dependency injection following Apple's KISS principle
"""
from typing import Dict, Any, Callable, Optional
import logging


class ServiceContainer:
    """Single, simple container implementation"""

    def __init__(self) -> None:
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def register_instance(self, name: str, instance: Any) -> None:
        """Register existing instance"""
        self._instances[name] = instance

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register factory function for transient objects"""
        self._factories[name] = factory

    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """Register singleton factory"""
        self._factories[name] = factory
        if name not in self._singletons:
            self._singletons[name] = None

    def get(self, name: str) -> Any:
        """Get service by name"""
        if name in self._instances:
            return self._instances[name]
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
        if name in self._factories:
            return self._factories[name]()
        raise KeyError(f"Service '{name}' not registered")

    def reset(self) -> None:
        """Reset all singletons (for testing)"""
        self._singletons = {k: None for k in self._singletons}


_container: Optional[ServiceContainer] = None

def get_container() -> ServiceContainer:
    """Get global container instance"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container
