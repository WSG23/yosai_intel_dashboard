# core/enhanced_container.py - FINAL: Industry-standard compliant container
"""
Enhanced DI Container with full industry standard compliance
Based on best practices from dependency-injector and modern Python DI patterns
"""

from typing import Dict, Any, TypeVar, Callable, Optional, List, Protocol, Type, Union
from dataclasses import dataclass, field
import threading
import logging
import weakref
import inspect
from contextlib import contextmanager
from enum import Enum

from .container import Container

T = TypeVar('T')
logger = logging.getLogger(__name__)

class LifecycleScope(Enum):
    """Service lifecycle scopes - industry standard"""
    SINGLETON = "singleton"       # One instance for entire application
    TRANSIENT = "transient"       # New instance every time
    REQUEST = "request"           # One instance per request (web apps)
    SESSION = "session"           # One instance per session (web apps)

class ServiceLifecycle(Protocol):
    """Protocol for services that need lifecycle management"""
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def configure(self, **kwargs) -> None: ...

@dataclass
class ServiceDefinition:
    """Enhanced service definition with industry standard features"""
    factory: Callable[..., Any]
    scope: LifecycleScope = LifecycleScope.SINGLETON
    dependencies: List[str] = field(default_factory=list)
    lazy: bool = True
    lifecycle: bool = False
    tags: List[str] = field(default_factory=list)  # NEW: Service tagging
    priority: int = 0  # NEW: Service priority for ordering
    config_section: Optional[str] = None  # NEW: Configuration binding

class EnhancedContainer(Container):
    """Industry-standard DI container with advanced features"""
    
    def __init__(self, name: str = "default"):
        super().__init__()
        self.name = name
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}  # NEW: Scoped instances
        self._lifecycle_services: List[Any] = []
        self._started = False
        self._current_scope: Optional[str] = None  # NEW: Current scope context
        self._event_handlers: Dict[str, List[Callable]] = {}  # NEW: Event system
    
    # NEW: Service registration with enhanced features
    def register(self, 
                 name: str, 
                 factory: Union[Callable[..., T], Type[T]], 
                 scope: LifecycleScope = LifecycleScope.SINGLETON,
                 dependencies: Optional[List[str]] = None,
                 lazy: bool = True,
                 lifecycle: bool = False,
                 tags: Optional[List[str]] = None,
                 priority: int = 0,
                 config_section: Optional[str] = None) -> None:
        """Enhanced service registration with full feature set"""
        
        # Auto-detect dependencies from type hints
        if dependencies is None:
            dependencies = self._auto_detect_dependencies(factory)
        
        self._services[name] = ServiceDefinition(
            factory=factory,
            scope=scope,
            dependencies=dependencies,
            lazy=lazy,
            lifecycle=lifecycle,
            tags=tags or [],
            priority=priority,
            config_section=config_section
        )
        
        self._emit_event('service_registered', name, self._services[name])
        logger.debug(f"Registered service: {name} (scope: {scope.value}, tags: {tags})")
    
    def _auto_detect_dependencies(self, factory: Callable) -> List[str]:
        """Auto-detect dependencies from type annotations - industry standard feature"""
        try:
            sig = inspect.signature(factory)
            dependencies = []
            
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    # Convert type annotation to service name
                    if hasattr(param.annotation, '__name__'):
                        service_name = param.annotation.__name__.lower()
                        if service_name in self._services:
                            dependencies.append(service_name)
            
            return dependencies
        except Exception as e:
            logger.warning(f"Could not auto-detect dependencies: {e}")
            return []
    
    # NEW: Scoped service resolution
    @contextmanager
    def scope(self, scope_name: str):
        """Context manager for scoped service resolution"""
        old_scope = self._current_scope
        self._current_scope = scope_name
        
        if scope_name not in self._scoped_instances:
            self._scoped_instances[scope_name] = {}
        
        try:
            yield self
        finally:
            self._current_scope = old_scope
            # Cleanup scope if needed
            if scope_name in self._scoped_instances:
                self._cleanup_scope(scope_name)
    
    def _cleanup_scope(self, scope_name: str) -> None:
        """Cleanup scoped instances"""
        if scope_name in self._scoped_instances:
            for instance in self._scoped_instances[scope_name].values():
                if hasattr(instance, 'cleanup'):
                    try:
                        instance.cleanup()
                    except Exception as e:
                        logger.error(f"Error cleaning up scoped instance: {e}")
            del self._scoped_instances[scope_name]
    
    def get(self, name: str, **kwargs) -> Any:
        """Enhanced service resolution with scoping support"""
        if name not in self._services and name not in self._instances:
            available = ', '.join(self.list_services())
            raise ValueError(f"Service '{name}' not registered. Available: {available}")
        
        # Return direct instance if available
        if name in self._instances:
            return self._instances[name]
        
        # Check circular dependencies
        if name in self._resolving:
            chain = ' -> '.join(self._resolving) + f' -> {name}'
            raise ValueError(f"Circular dependency detected: {chain}")
        
        service_def = self._services[name]
        
        # Handle different scopes
        if service_def.scope == LifecycleScope.SINGLETON:
            if name in self._instances:
                return self._instances[name]
        elif service_def.scope in [LifecycleScope.REQUEST, LifecycleScope.SESSION]:
            if self._current_scope and self._current_scope in self._scoped_instances:
                scoped_instances = self._scoped_instances[self._current_scope]
                if name in scoped_instances:
                    return scoped_instances[name]
        
        # Create new instance
        with self._lock:
            self._resolving.add(name)
            try:
                # Resolve dependencies with enhanced error context
                dependencies = {}
                for dep_name in service_def.dependencies:
                    try:
                        dependencies[dep_name] = self.get(dep_name)
                    except Exception as e:
                        raise ValueError(f"Failed to resolve dependency '{dep_name}' for service '{name}': {e}")
                
                # Add configuration if specified
                if service_def.config_section:
                    config = self.get_optional('config')
                    if config and hasattr(config, service_def.config_section):
                        dependencies['config'] = getattr(config, service_def.config_section)
                
                # Add any additional kwargs
                dependencies.update(kwargs)
                
                logger.debug(f"Creating instance of: {name}")
                instance = service_def.factory(**dependencies)
                
                # Configure instance if it supports configuration
                if hasattr(instance, 'configure'):
                    instance.configure(**kwargs)
                
                # Handle lifecycle services
                if service_def.lifecycle and hasattr(instance, 'start'):
                    self._lifecycle_services.append(weakref.ref(instance))
                    if self._started:
                        instance.start()
                
                # Store instance based on scope
                if service_def.scope == LifecycleScope.SINGLETON:
                    self._instances[name] = instance
                elif service_def.scope in [LifecycleScope.REQUEST, LifecycleScope.SESSION]:
                    if self._current_scope:
                        self._scoped_instances[self._current_scope][name] = instance
                
                self._emit_event('service_created', name, instance)
                return instance
                
            finally:
                self._resolving.discard(name)
    
    # NEW: Service discovery by tags
    def get_services_by_tag(self, tag: str) -> List[Any]:
        """Get all services with a specific tag"""
        services = []
        for name, service_def in self._services.items():
            if tag in service_def.tags:
                try:
                    services.append(self.get(name))
                except Exception as e:
                    logger.warning(f"Could not resolve service {name} with tag {tag}: {e}")
        return services
    
    # NEW: Configuration binding
    def bind_configuration(self, config_data: Dict[str, Any]) -> None:
        """Bind configuration data to services"""
        for name, service_def in self._services.items():
            if service_def.config_section and service_def.config_section in config_data:
                # Store config for later injection
                config_key = f"_config_{service_def.config_section}"
                self.register_instance(config_key, config_data[service_def.config_section])
    
    # NEW: Event system for monitoring
    def on(self, event: str, handler: Callable) -> None:
        """Register event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def _emit_event(self, event: str, *args, **kwargs) -> None:
        """Emit event to handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in event handler for {event}: {e}")
    
    # NEW: Enhanced diagnostics
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get dependency graph for visualization"""
        graph = {}
        for name, service_def in self._services.items():
            graph[name] = service_def.dependencies.copy()
        return graph
    
    def get_service_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a service"""
        if name not in self._services:
            return {}
        
        service_def = self._services[name]
        return {
            'name': name,
            'scope': service_def.scope.value,
            'dependencies': service_def.dependencies,
            'tags': service_def.tags,
            'priority': service_def.priority,
            'lifecycle': service_def.lifecycle,
            'lazy': service_def.lazy,
            'instantiated': name in self._instances,
            'config_section': service_def.config_section
        }
    
    # Enhanced health check with detailed diagnostics
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check with detailed diagnostics"""
        try:
            # Basic metrics
            health = {
                'status': 'healthy',
                'container_name': self.name,
                'services_registered': len(self._services),
                'instances_created': len(self._instances),
                'scoped_instances': {
                    scope: len(instances) 
                    for scope, instances in self._scoped_instances.items()
                },
                'lifecycle_services': len(self._lifecycle_services),
                'started': self._started,
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
            
            # Service health check
            unhealthy_services = []
            for name, service_def in self._services.items():
                try:
                    if not service_def.lazy and name not in self._instances:
                        # Try to create the service
                        self.get(name)
                except Exception as e:
                    unhealthy_services.append({
                        'name': name,
                        'error': str(e)
                    })
            
            if unhealthy_services:
                health['status'] = 'degraded'
                health['unhealthy_services'] = unhealthy_services
            
            # Dependency cycle detection
            cycles = self._detect_dependency_cycles()
            if cycles:
                health['status'] = 'unhealthy'
                health['dependency_cycles'] = cycles
            
            return health
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
    
    def _detect_dependency_cycles(self) -> List[List[str]]:
        """Detect dependency cycles in service graph"""
        def dfs(node: str, path: List[str], visited: set, cycles: List[List[str]]) -> None:
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited or node not in self._services:
                return
            
            visited.add(node)
            path.append(node)
            
            for dep in self._services[node].dependencies:
                dfs(dep, path, visited, cycles)
            
            path.pop()
        
        cycles = []
        visited = set()
        
        for service_name in self._services:
            if service_name not in visited:
                dfs(service_name, [], visited, cycles)
        
        return cycles

# ============================================================================
# core/providers.py - NEW: Provider system for different service types
"""
Provider system inspired by dependency-injector for different service types
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional
import logging

logger = logging.getLogger(__name__)

class Provider(ABC):
    """Base provider interface"""
    
    @abstractmethod
    def provide(self, container: 'EnhancedContainer', **kwargs) -> Any:
        """Provide the service instance"""
        pass

class FactoryProvider(Provider):
    """Provider for factory-created services"""
    
    def __init__(self, factory: Callable, dependencies: Optional[List[str]] = None):
        self.factory = factory
        self.dependencies = dependencies or []
    
    def provide(self, container: 'EnhancedContainer', **kwargs) -> Any:
        """Create new instance every time"""
        resolved_deps = {}
        for dep in self.dependencies:
            resolved_deps[dep] = container.get(dep)
        
        resolved_deps.update(kwargs)
        return self.factory(**resolved_deps)

class SingletonProvider(Provider):
    """Provider for singleton services"""
    
    def __init__(self, factory: Callable, dependencies: Optional[List[str]] = None):
        self.factory = factory
        self.dependencies = dependencies or []
        self._instance = None
        self._lock = threading.Lock()
    
    def provide(self, container: 'EnhancedContainer', **kwargs) -> Any:
        """Return singleton instance"""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    resolved_deps = {}
                    for dep in self.dependencies:
                        resolved_deps[dep] = container.get(dep)
                    
                    resolved_deps.update(kwargs)
                    self._instance = self.factory(**resolved_deps)
        
        return self._instance

class ConfigurationProvider(Provider):
    """Provider for configuration-based services"""
    
    def __init__(self, config_section: str, factory: Optional[Callable] = None):
        self.config_section = config_section
        self.factory = factory
    
    def provide(self, container: 'EnhancedContainer', **kwargs) -> Any:
        """Provide configuration data or configured service"""
        config = container.get('config')
        
        if hasattr(config, self.config_section):
            config_data = getattr(config, self.config_section)
            
            if self.factory:
                return self.factory(config_data, **kwargs)
            else:
                return config_data
        else:
            raise ValueError(f"Configuration section '{self.config_section}' not found")

# ============================================================================
# Usage Example - core/service_registry_enhanced.py
"""
Enhanced service registry using the new container features
"""

from .enhanced_container import EnhancedContainer, LifecycleScope
from .service_registry import (
    create_database_with_yaml_config,
    create_cache_with_yaml_config,
    create_analytics_service_with_config,
)

def create_production_container() -> EnhancedContainer:
    """Create production-ready container with all features"""
    container = EnhancedContainer("production")
    
    # Register configuration with binding
    container.register(
        'config',
        ConfigurationProvider('app_config'),
        scope=LifecycleScope.SINGLETON,
        tags=['core', 'config']
    )
    
    # Register database with lifecycle management
    container.register(
        'database',
        create_database_with_yaml_config,
        scope=LifecycleScope.SINGLETON,
        dependencies=['config'],
        lifecycle=True,
        tags=['infrastructure', 'database'],
        config_section='database'
    )
    
    # Register cache manager with request scope for web apps
    container.register(
        'cache_manager',
        create_cache_with_yaml_config,
        scope=LifecycleScope.REQUEST,
        dependencies=['config'],
        lifecycle=True,
        tags=['infrastructure', 'cache']
    )
    
    # Register analytics service with high priority
    container.register(
        'analytics_service',
        create_analytics_service_with_config,
        scope=LifecycleScope.SINGLETON,
        dependencies=['access_model', 'anomaly_model', 'config', 'cache_manager'],
        tags=['business', 'analytics'],
        priority=100
    )
    
    # Event monitoring
    container.on('service_created', lambda name, instance: logger.info(f"Service created: {name}"))
    container.on('service_registered', lambda name, service_def: logger.debug(f"Service registered: {name}"))
    
    return container

# ============================================================================
# tests/test_enhanced_container.py - NEW: Comprehensive testing
"""
Comprehensive tests for the enhanced container
"""

import unittest
from core.enhanced_container import EnhancedContainer, LifecycleScope

class TestEnhancedContainer(unittest.TestCase):
    """Test enhanced container features"""
    
    def setUp(self):
        self.container = EnhancedContainer("test")
    
    def test_scoped_services(self):
        """Test scoped service resolution"""
        # Register request-scoped service
        self.container.register(
            'request_service',
            lambda: f"request_{id(object())}",
            scope=LifecycleScope.REQUEST
        )
        
        # Test different scopes return different instances
        with self.container.scope('request_1'):
            service1 = self.container.get('request_service')
        
        with self.container.scope('request_2'):
            service2 = self.container.get('request_service')
        
        self.assertNotEqual(service1, service2)
    
    def test_service_tags(self):
        """Test service discovery by tags"""
        self.container.register('service1', lambda: "service1", tags=['web'])
        self.container.register('service2', lambda: "service2", tags=['web'])
        self.container.register('service3', lambda: "service3", tags=['data'])
        
        web_services = self.container.get_services_by_tag('web')
        self.assertEqual(len(web_services), 2)
        self.assertIn("service1", web_services)
        self.assertIn("service2", web_services)
    
    def test_dependency_cycle_detection(self):
        """Test dependency cycle detection"""
        self.container.register('a', lambda b: f"a-{b}", dependencies=['b'])
        self.container.register('b', lambda c: f"b-{c}", dependencies=['c'])
        self.container.register('c', lambda a: f"c-{a}", dependencies=['a'])
        
        health = self.container.health_check()
        self.assertEqual(health['status'], 'unhealthy')
        self.assertIn('dependency_cycles', health)

def run_enhanced_tests():
    """Run enhanced container tests"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEnhancedContainer))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Running Enhanced DI Container Tests...")
    success = run_enhanced_tests()
    
    if success:
        print("✅ Enhanced container tests passed!")
    else:
        print("❌ Some enhanced tests failed")