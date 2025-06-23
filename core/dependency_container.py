"""Dependency injection container following Apple's modular design principles"""
from typing import Dict, Type, TypeVar, Callable, Any
import logging

T = TypeVar('T')

class ServiceContainer:
    """Thread-safe dependency injection container"""
    def __init__(self) -> None:
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Callable[[], Any]] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._logger = logging.getLogger(__name__)

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        self._singletons[interface] = implementation

    def register_transient(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a transient service with factory"""
        self._factories[interface] = factory

    def get(self, interface: Type[T]) -> T:
        """Resolve service dependency"""
        if interface in self._services:
            return self._services[interface]
        if interface in self._singletons:
            instance = self._singletons[interface]()
            self._services[interface] = instance
            return instance
        if interface in self._factories:
            return self._factories[interface]()
        raise ValueError(f"Service {interface.__name__} not registered")

    def has(self, interface: Type[T]) -> bool:
        return interface in self._singletons or interface in self._factories or interface in self._services
