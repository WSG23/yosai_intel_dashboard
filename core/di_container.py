# core/di_container.py
"""
Clean Dependency Injection Container - Fixed Circular Dependencies
Modular, testable, and production-ready implementation
"""
from typing import Dict, Any, TypeVar, Callable, Optional, List, Set
from dataclasses import dataclass, field
import threading
import logging
from abc import ABC, abstractmethod
from enum import Enum
import time

T = TypeVar('T')
logger = logging.getLogger(__name__)

class ServiceScope(Enum):
    """Service lifecycle scopes"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class ServiceStatus(Enum):
    """Service registration status"""
    REGISTERED = "registered"
    CREATING = "creating"
    CREATED = "created"
    FAILED = "failed"

@dataclass
class ServiceDefinition:
    """Clean service definition with clear separation of concerns"""
    name: str
    factory: Callable[..., Any]
    scope: ServiceScope = ServiceScope.SINGLETON
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    priority: int = 0
    status: ServiceStatus = ServiceStatus.REGISTERED

class ServiceLayer(Enum):
    """Layered architecture to prevent circular dependencies"""
    FOUNDATION = 0      # Config, logging, basic infrastructure
    INFRASTRUCTURE = 1  # Database, cache, external connections
    MODELS = 2         # Data models and repositories
    SERVICES = 3       # Business logic services
    CONTROLLERS = 4    # Web controllers, APIs
    MONITORING = 5     # Health checks, metrics (top layer)

@dataclass
class LayeredServiceDefinition(ServiceDefinition):
    """Service definition with layer information"""
    layer: ServiceLayer = ServiceLayer.SERVICES

class DIContainer:
    """Production-ready Dependency Injection Container
    
    Features:
    - Layered architecture prevents circular dependencies
    - Thread-safe singleton management
    - Clear error messages with dependency chains
    - Modular service registration
    - Health monitoring and diagnostics
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self._services: Dict[str, LayeredServiceDefinition] = {}
        self._instances: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._resolution_stack: List[str] = []
        self._startup_order: List[str] = []
        self._health_checks: Dict[str, Callable[[], bool]] = {}
        
        # Register self for diagnostics
        self.register_instance("container", self)
        
    def register(self,
                 name: str,
                 factory: Callable[..., T],
                 scope: ServiceScope = ServiceScope.SINGLETON,
                 dependencies: Optional[List[str]] = None,
                 layer: ServiceLayer = ServiceLayer.SERVICES,
                 tags: Optional[Set[str]] = None,
                 priority: int = 0) -> None:
        """Register a service with the container"""
        
        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered")
            
        # Validate dependencies don't create cycles in layers
        deps = dependencies or []
        for dep in deps:
            if dep in self._services:
                dep_layer = self._services[dep].layer
                if dep_layer.value > layer.value:
                    raise ValueError(
                        f"Invalid layer dependency: {name} (layer {layer.name}) "
                        f"cannot depend on {dep} (layer {dep_layer.name}). "
                        f"Dependencies must be from lower or same layer."
                    )
        
        service_def = LayeredServiceDefinition(
            name=name,
            factory=factory,
            scope=scope,
            dependencies=deps,
            layer=layer,
            tags=tags or set(),
            priority=priority
        )
        
        self._services[name] = service_def
        logger.debug(f"Registered service '{name}' in layer {layer.name}")
    
    def register_instance(self, name: str, instance: Any) -> None:
        """Register an existing instance"""
        self._instances[name] = instance
        logger.debug(f"Registered instance: {name}")
    
    def get(self, name: str) -> Any:
        """Get a service instance with clear error reporting"""
        if name not in self._services and name not in self._instances:
            available = list(self._services.keys()) + list(self._instances.keys())
            raise ValueError(f"Service '{name}' not registered. Available: {available}")
        
        # Return existing instance if available
        if name in self._instances:
            return self._instances[name]
        
        # Check for circular dependencies
        if name in self._resolution_stack:
            cycle_chain = " -> ".join(self._resolution_stack) + f" -> {name}"
            raise ValueError(f"Circular dependency detected: {cycle_chain}")
        
        service_def = self._services[name]
        
        # Return cached instance for singletons
        if service_def.scope == ServiceScope.SINGLETON and name in self._instances:
            return self._instances[name]
        
        # Create new instance with clear error context
        with self._lock:
            self._resolution_stack.append(name)
            service_def.status = ServiceStatus.CREATING
            
            try:
                # Resolve dependencies with enhanced error reporting
                dependencies = {}
                for dep_name in service_def.dependencies:
                    try:
                        dependencies[dep_name] = self.get(dep_name)
                    except Exception as e:
                        raise ValueError(
                            f"Failed to resolve dependency '{dep_name}' for service '{name}': {e}"
                        ) from e
                
                # Create instance
                logger.debug(f"Creating instance of: {name}")
                instance = service_def.factory(**dependencies)
                
                # Cache singleton instances
                if service_def.scope == ServiceScope.SINGLETON:
                    self._instances[name] = instance
                
                # Track startup order for monitoring
                if name not in self._startup_order:
                    self._startup_order.append(name)
                
                service_def.status = ServiceStatus.CREATED
                logger.debug(f"Successfully created service: {name}")
                
                return instance
                
            except Exception as e:
                service_def.status = ServiceStatus.FAILED
                logger.error(f"Failed to create service '{name}': {e}")
                raise
            finally:
                self._resolution_stack.pop()
    
    def get_optional(self, name: str) -> Optional[Any]:
        """Get a service instance, returning None if not available"""
        try:
            return self.get(name)
        except ValueError:
            return None
    
    def start_lifecycle_services(self) -> None:
        """Start all lifecycle-managed services in layer order"""
        services_by_layer = {}
        for service_def in self._services.values():
            layer = service_def.layer
            if layer not in services_by_layer:
                services_by_layer[layer] = []
            services_by_layer[layer].append(service_def)
        
        # Start services layer by layer, priority within layer
        for layer in sorted(services_by_layer.keys(), key=lambda x: x.value):
            layer_services = sorted(services_by_layer[layer], key=lambda x: x.priority, reverse=True)
            
            for service_def in layer_services:
                try:
                    instance = self.get(service_def.name)
                    if hasattr(instance, 'start'):
                        instance.start()
                        logger.info(f"Started service: {service_def.name}")
                except Exception as e:
                    logger.error(f"Failed to start service {service_def.name}: {e}")
    
    def stop_lifecycle_services(self) -> None:
        """Stop all lifecycle-managed services in reverse layer order"""
        for service_name in reversed(self._startup_order):
            try:
                if service_name in self._instances:
                    instance = self._instances[service_name]
                    if hasattr(instance, 'stop'):
                        instance.stop()
                        logger.info(f"Stopped service: {service_name}")
            except Exception as e:
                logger.error(f"Failed to stop service {service_name}: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all services"""
        health = {
            'container': self.name,
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {},
            'layers': {},
            'dependency_graph': self._build_dependency_graph(),
            'startup_order': self._startup_order.copy()
        }
        
        # Check each service
        for service_name, service_def in self._services.items():
            service_health = {
                'status': service_def.status.value,
                'layer': service_def.layer.name,
                'dependencies': service_def.dependencies.copy(),
                'tags': list(service_def.tags)
            }
            
            # Try to instantiate if not already created
            if service_def.status == ServiceStatus.REGISTERED:
                try:
                    self.get(service_name)
                    service_health['status'] = 'healthy'
                except Exception as e:
                    service_health['status'] = 'unhealthy'
                    service_health['error'] = str(e)
                    health['status'] = 'degraded'
            
            health['services'][service_name] = service_health
        
        # Layer summary
        for layer in ServiceLayer:
            layer_services = [s for s in self._services.values() if s.layer == layer]
            health['layers'][layer.name] = {
                'count': len(layer_services),
                'services': [s.name for s in layer_services]
            }
        
        return health
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph for visualization"""
        return {name: service.dependencies.copy() for name, service in self._services.items()}
    
    def clear(self) -> None:
        """Clear all services and instances"""
        self.stop_lifecycle_services()
        self._services.clear()
        self._instances.clear()
        self._resolution_stack.clear()
        self._startup_order.clear()
        logger.info(f"Container '{self.name}' cleared")
    
    def get_services_by_layer(self, layer: ServiceLayer) -> List[str]:
        """Get all services in a specific layer"""
        return [name for name, service in self._services.items() if service.layer == layer]
    
    def get_services_by_tag(self, tag: str) -> List[str]:
        """Get all services with a specific tag"""
        return [name for name, service in self._services.items() if tag in service.tags]

# Global container instance
_default_container: Optional[DIContainer] = None
_container_lock = threading.Lock()

def get_container() -> DIContainer:
    """Get the default container instance (thread-safe singleton)"""
    global _default_container
    if _default_container is None:
        with _container_lock:
            if _default_container is None:
                _default_container = DIContainer("default")
    return _default_container

def reset_container() -> None:
    """Reset the default container (mainly for testing)"""
    global _default_container
    with _container_lock:
        if _default_container:
            _default_container.clear()
        _default_container = None

def create_container(name: str) -> DIContainer:
    """Create a new named container"""
    return DIContainer(name)