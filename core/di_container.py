"""Enhanced Dependency Injection Container"""

from typing import Dict, Type, TypeVar, Callable, Any, Optional
from dataclasses import dataclass
import inspect
import threading


T = TypeVar("T")


@dataclass
class ServiceRegistration:
    """Service registration configuration"""

    service_class: Type
    singleton: bool = True
    factory: Optional[Callable] = None
    dependencies: Optional[list] = None


class DIContainer:
    """Enhanced thread-safe dependency injection container"""

    def __init__(self) -> None:
        self._services: Dict[str, ServiceRegistration] = {}
        self._instances: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def register(
        self,
        interface: Type[T],
        implementation: Type[T],
        singleton: bool = True,
        factory: Optional[Callable] = None,
    ) -> None:
        """Register a service with the container"""

        with self._lock:
            service_name = interface.__name__
            self._services[service_name] = ServiceRegistration(
                service_class=implementation,
                singleton=singleton,
                factory=factory,
                dependencies=self._get_dependencies(implementation),
            )

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service instance"""

        with self._lock:
            service_name = interface.__name__

            if service_name not in self._services:
                raise ValueError(f"Service {service_name} not registered")

            registration = self._services[service_name]

            if registration.singleton and service_name in self._instances:
                return self._instances[service_name]  # type: ignore[return-value]

            instance = self._create_instance(registration)

            if registration.singleton:
                self._instances[service_name] = instance

            return instance

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create service instance with dependency injection"""

        if registration.factory:
            return registration.factory()

        if registration.dependencies:
            deps = [self.resolve(dep_type) for dep_type in registration.dependencies]
            return registration.service_class(*deps)

        return registration.service_class()

    def _get_dependencies(self, service_class: Type) -> list:
        """Extract constructor dependencies from type hints"""

        sig = inspect.signature(service_class.__init__)
        dependencies = []
        for param_name, param in sig.parameters.items():
            if param_name != "self" and param.annotation != inspect.Parameter.empty:
                dependencies.append(param.annotation)

        return dependencies

