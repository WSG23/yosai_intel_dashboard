"""Simple dependency injection container for tests."""
from typing import Callable, Any, Dict

class Container:
    """Basic container supporting factories, singletons and instances."""

    def __init__(self) -> None:
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}

    def register_instance(self, name: str, instance: Any) -> None:
        self._instances[name] = instance

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        self._factories[name] = factory

    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        self._factories[name] = factory
        self._singletons[name] = None

    def get(self, name: str) -> Any:
        if name in self._instances:
            return self._instances[name]
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
        if name in self._factories:
            return self._factories[name]()
        raise KeyError(name)

    def reset_singletons(self) -> None:
        for key in self._singletons:
            self._singletons[key] = None

class TestContainer(Container):
    """Container used as context manager for tests."""

    def __enter__(self) -> 'TestContainer':
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._instances.clear()
        self._factories.clear()
        self._singletons.clear()
