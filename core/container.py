# core/container.py
"""Dependency Injection Container for Yōsai Intel Dashboard"""
from typing import Dict, Any, TypeVar, Callable, Optional, List
from dataclasses import dataclass, field
import threading
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)

@dataclass
class ServiceDefinition:
    """Definition of a registered service"""
    factory: Callable[..., Any]
    singleton: bool = True
    dependencies: List[str] = field(default_factory=list)

class Container:
    """Simple but powerful dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._instances: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._resolving: set = set()  # Prevent circular dependencies
    
    def register(self, 
                 name: str, 
                 factory: Callable[..., T], 
                 singleton: bool = True,
                 dependencies: Optional[List[str]] = None) -> None:
        """Register a service with the container"""
        self._services[name] = ServiceDefinition(
            factory=factory,
            singleton=singleton,
            dependencies=dependencies or []
        )
        logger.debug(f"Registered service: {name}")
    
    def register_instance(self, name: str, instance: Any) -> None:
        """Register an existing instance"""
        self._instances[name] = instance
        logger.debug(f"Registered instance: {name}")
    
    def get(self, name: str) -> Any:
        """Get a service instance"""
        if name not in self._services and name not in self._instances:
            raise ValueError(f"Service '{name}' not registered")
        
        # Return existing instance if available
        if name in self._instances:
            return self._instances[name]
        
        # Check for circular dependencies
        if name in self._resolving:
            raise ValueError(f"Circular dependency detected for service '{name}'")
        
        service_def = self._services[name]
        
        # Return cached instance for singletons
        if service_def.singleton and name in self._instances:
            return self._instances[name]
        
        # Create new instance
        with self._lock:
            self._resolving.add(name)
            try:
                # Resolve dependencies
                dependencies = {}
                for dep_name in service_def.dependencies:
                    dependencies[dep_name] = self.get(dep_name)
                
                # Create instance
                logger.debug(f"Creating instance of: {name}")
                instance = service_def.factory(**dependencies)
                
                # Cache if singleton
                if service_def.singleton:
                    self._instances[name] = instance
                
                return instance
                
            finally:
                self._resolving.discard(name)
    
    def get_optional(self, name: str) -> Optional[Any]:
        """Get a service, return None if not found"""
        try:
            return self.get(name)
        except ValueError:
            return None
    
    def has(self, name: str) -> bool:
        """Check if service is registered"""
        return name in self._services or name in self._instances
    
    def clear(self) -> None:
        """Clear all registered services and instances"""
        self._services.clear()
        self._instances.clear()
        logger.debug("Container cleared")
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self._services.keys()) + list(self._instances.keys())

# Global container instance
_container: Optional[Container] = None

def get_container() -> Container:
    """Get the global container instance"""
    global _container
    if _container is None:
        _container = Container()
    return _container

def reset_container() -> None:
    """Reset the global container (useful for testing)"""
    global _container
    _container = None