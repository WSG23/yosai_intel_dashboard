"""Unified Dependency Injection Container"""

import logging
from typing import Dict, Any, Callable, Optional, TypeVar, List
from contextlib import contextmanager
import threading

T = TypeVar('T')
logger = logging.getLogger(__name__)


class DIContainer:
    """Thread-safe dependency injection container with lifecycle hooks"""

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._services: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        self._lifecycle_hooks: Dict[str, List[Callable]] = {
            'before_create': [],
            'after_create': [],
            'before_destroy': [],
            'after_destroy': []
        }

    def register(self, name: str, factory: Callable, *, singleton: bool = False, dependencies: Optional[List[str]] = None) -> None:
        """Register a service with the container"""
        with self._lock:
            self._services[name] = factory
            self._dependencies[name] = dependencies or []
            if singleton and not dependencies:
                try:
                    instance = factory()
                    self._singletons[name] = instance
                    self._run_hooks('after_create', name, instance)
                except Exception as exc:
                    logger.error("Failed to create singleton %s: %s", name, exc)

    def register_instance(self, name: str, instance: Any) -> None:
        with self._lock:
            self._instances[name] = instance

    def get(self, name: str) -> Any:
        with self._lock:
            if name in self._instances:
                return self._instances[name]
            if name in self._singletons:
                return self._singletons[name]
            if name in self._services:
                return self._create_instance(name)
            raise ValueError(f"Service not registered: {name}")

    def get_optional(self, name: str) -> Optional[Any]:
        try:
            return self.get(name)
        except ValueError:
            return None

    def has(self, name: str) -> bool:
        return name in self._services or name in self._instances or name in self._singletons

    def _create_instance(self, name: str) -> Any:
        factory = self._services[name]
        deps = {dep: self.get(dep) for dep in self._dependencies.get(name, [])}
        self._run_hooks('before_create', name, None)
        instance = factory(**deps)
        if name in self._singletons:
            self._singletons[name] = instance
        self._run_hooks('after_create', name, instance)
        return instance

    def add_lifecycle_hook(self, event: str, callback: Callable) -> None:
        if event in self._lifecycle_hooks:
            self._lifecycle_hooks[event].append(callback)

    def _run_hooks(self, event: str, name: str, instance: Any) -> None:
        for hook in self._lifecycle_hooks.get(event, []):
            try:
                hook(name, instance)
            except Exception as exc:
                logger.warning("Lifecycle hook failed for %s: %s", event, exc)

    def health_check(self) -> Dict[str, Any]:
        with self._lock:
            status = {
                'container': self.name,
                'services_registered': len(self._services),
                'instances_created': len(self._instances),
                'singletons_created': len(self._singletons),
                'services': {}
            }
            for name in self._services:
                try:
                    instance = self.get_optional(name)
                    status['services'][name] = {
                        'status': 'healthy' if instance else 'unavailable',
                        'type': type(instance).__name__ if instance else 'None'
                    }
                except Exception as exc:
                    status['services'][name] = {'status': 'error', 'error': str(exc)}
            return status
