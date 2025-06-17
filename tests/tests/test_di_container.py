# tests/test_di_container.py - NEW: Testing utilities for DI system
"""
Testing utilities and test cases for the Dependency Injection system
"""

import unittest
from unittest.mock import Mock, patch
import threading
import time
from typing import Any, Dict

from core.container import Container, ServiceDefinition
from core.service_registry import (
    configure_container_with_yaml,
    get_configured_container_with_yaml as get_configured_container,
)
from core.config_manager import ConfigManager

class MockService:
    """Mock service for testing"""
    def __init__(self, name: str = "mock"):
        self.name = name
        self.started = False
        self.stopped = False
    
    def start(self) -> None:
        self.started = True
    
    def stop(self) -> None:
        self.stopped = True

class TestContainer(unittest.TestCase):
    """Test the DI container functionality"""
    
    def setUp(self):
        self.container = Container()
    
    def tearDown(self):
        self.container.clear()
    
    def test_service_registration(self):
        """Test basic service registration and retrieval"""
        # Register a simple service
        self.container.register('test_service', lambda: MockService("test"))
        
        # Retrieve the service
        service = self.container.get('test_service')
        self.assertIsInstance(service, MockService)
        self.assertEqual(service.name, "test")
    
    def test_singleton_behavior(self):
        """Test that singletons return the same instance"""
        self.container.register('singleton_service', lambda: MockService("singleton"))
        
        service1 = self.container.get('singleton_service')
        service2 = self.container.get('singleton_service')
        
        self.assertIs(service1, service2)
    
    def test_dependency_injection(self):
        """Test dependency injection between services"""
        # Register dependent services
        self.container.register('dependency', lambda: MockService("dependency"))
        self.container.register(
            'main_service', 
            lambda dependency: MockService(f"main_with_{dependency.name}"),
            dependencies=['dependency']
        )
        
        service = self.container.get('main_service')
        self.assertEqual(service.name, "main_with_dependency")
    
    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected"""
        self.container.register(
            'service_a',
            lambda service_b: MockService("a"),
            dependencies=['service_b']
        )
        self.container.register(
            'service_b',
            lambda service_a: MockService("b"),
            dependencies=['service_a']
        )
        
        with self.assertRaises(ValueError) as context:
            self.container.get('service_a')
        
        self.assertIn("Circular dependency", str(context.exception))
    
    def test_service_not_found(self):
        """Test error when service is not registered"""
        with self.assertRaises(ValueError) as context:
            self.container.get('non_existent_service')
        
        self.assertIn("not registered", str(context.exception))
        self.assertIn("Available:", str(context.exception))
    
    def test_lifecycle_management(self):
        """Test service lifecycle management"""
        self.container.register(
            'lifecycle_service',
            lambda: MockService("lifecycle"),
            lifecycle=True
        )
        
        # Get the service
        service = self.container.get('lifecycle_service')
        self.assertFalse(service.started)
        
        # Start container
        self.container.start()
        self.assertTrue(service.started)
        
        # Stop container
        self.container.stop()
        self.assertTrue(service.stopped)
    
    def test_thread_safety(self):
        """Test that container is thread-safe"""
        results = []
        
        def create_service():
            service = self.container.get('thread_service')
            results.append(service)
        
        self.container.register('thread_service', lambda: MockService("thread"))
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_service)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All results should be the same instance (singleton)
        first_service = results[0]
        for service in results:
            self.assertIs(service, first_service)
    
    def test_health_check(self):
        """Test container health check"""
        self.container.register('test_service', lambda: MockService())
        
        health = self.container.health_check()
        
        self.assertEqual(health['status'], 'healthy')
        self.assertGreater(health['services_registered'], 0)
    
    def test_scope_manager(self):
        """Test test scope context manager"""
        # Register a service
        self.container.register('original_service', lambda: MockService("original"))
        original_service = self.container.get('original_service')
        
        # Use test scope
        with self.container.test_scope():
            # Register a different service with same name
            self.container.register('original_service', lambda: MockService("test"))
            test_service = self.container.get('original_service')
            
            # Should be different service
            self.assertNotEqual(original_service.name, test_service.name)
        
        # After scope, should be back to original
        restored_service = self.container.get('original_service')
        self.assertIs(restored_service, original_service)

class TestServiceRegistry(unittest.TestCase):
    """Test the service registry configuration"""
    
    def setUp(self):
        self.container = Container()
    
    def tearDown(self):
        self.container.clear()
    
    def test_full_container_configuration(self):
        """Test that all services can be configured"""
        configure_container_with_yaml(self.container)
        
        # Check that key services are registered
        essential_services = ['config', 'database', 'cache_manager']
        
        for service_name in essential_services:
            self.assertTrue(self.container.has(service_name))
    
    def test_service_dependency_resolution(self):
        """Test that services resolve their dependencies correctly"""
        configure_container_with_yaml(self.container)
        
        # These should not raise exceptions
        config = self.container.get('config')
        self.assertIsNotNone(config)
        
        database = self.container.get('database')
        self.assertIsNotNone(database)
        
        analytics_service = self.container.get('analytics_service')
        self.assertIsNotNone(analytics_service)

class DITestUtilities:
    """Utilities for testing with dependency injection"""
    
    @staticmethod
    def create_test_container() -> Container:
        """Create a container configured for testing"""
        container = Container()
        
        # Register mock services
        container.register('config', lambda: MockConfigManager())
        container.register('database', lambda: MockDatabase())
        container.register('cache_manager', lambda: MockCacheManager())
        
        return container
    
    @staticmethod
    def create_mock_app_with_container(container: Container) -> Mock:
        """Create a mock app with container access methods"""
        app = Mock()
        app.get_service = lambda name: container.get(name)
        app.get_service_optional = lambda name: container.get_optional(name)
        app.container_health = lambda: container.health_check()
        return app

class MockConfigManager:
    """Mock config manager for testing"""
    def __init__(self):
        self.app_config = Mock()
        self.app_config.debug = True
        self.app_config.host = "127.0.0.1"
        self.app_config.port = 8050

class MockDatabase:
    """Mock database for testing"""
    def execute_query(self, query: str, params=None):
        import pandas as pd
        return pd.DataFrame({'test': [1, 2, 3]})
    
    def execute_command(self, command: str, params=None):
        pass

class MockCacheManager:
    """Mock cache manager for testing"""
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str):
        return self._cache.get(key)
    
    def set(self, key: str, value):
        self._cache[key] = value
    
    def clear(self):
        self._cache.clear()

# ============================================================================
# core/callback_manager.py - ENHANCED: Better DI container access
"""
Enhanced callback manager with improved DI container access
"""

from typing import Any, Optional, Callable
import logging
from functools import wraps
from core.component_registry import ComponentRegistry
from core.layout_manager import LayoutManager
from core.container import Container

logger = logging.getLogger(__name__)

def inject_services(*service_names: str):
    """Decorator to inject services into callback functions"""
    def decorator(callback_func: Callable) -> Callable:
        @wraps(callback_func)
        def wrapper(*args, **kwargs):
            # Get container from current app context
            from dash import callback_context
            
            if hasattr(callback_context, 'triggered_prop_ids'):
                # We're in a callback context, try to get app
                try:
                    import dash
                    current_app = dash.current_app
                    
                    if hasattr(current_app, 'get_service'):
                        # Inject requested services
                        services = {}
                        for service_name in service_names:
                            try:
                                services[service_name] = current_app.get_service(service_name)
                            except Exception as e:
                                logger.warning(f"Could not inject service {service_name}: {e}")
                                services[service_name] = None
                        
                        # Add services to kwargs
                        kwargs.update(services)
                
                except Exception as e:
                    logger.warning(f"Could not inject services: {e}")
            
            return callback_func(*args, **kwargs)
        return wrapper
    return decorator

class CallbackManager:
    """Enhanced callback manager with better DI integration"""
    
    def __init__(self, app: Any, component_registry: ComponentRegistry, 
                 layout_manager: LayoutManager, container: Container):
        self.app = app
        self.registry = component_registry
        self.layout_manager = layout_manager
        self.container = container
        
        # Add container access methods to app if not already present
        if not hasattr(app, 'get_service'):
            app.get_service = lambda name: container.get(name)
            app.get_service_optional = lambda name: container.get_optional(name)
            app.container_health = lambda: container.health_check()
    
    def register_all_callbacks(self) -> None:
        """Register all callbacks with enhanced DI support"""
        try:
            self._register_page_routing_callback()
            self._register_component_callbacks()
            self._register_analytics_callbacks()
            self._register_navbar_callback()
            self._register_health_callbacks()  # NEW: Health monitoring
            
            logger.info("All callbacks registered successfully with enhanced DI")
            
        except Exception as e:
            logger.error(f"Error registering callbacks: {e}")
    
    def _register_health_callbacks(self) -> None:
        """Register health monitoring callbacks"""
        try:
            from dash import Output, Input, html
            import dash_bootstrap_components as dbc
            
            @self.app.callback(
                Output('system-health-indicator', 'children'),
                Input('health-check-interval', 'n_intervals'),
                prevent_initial_call=False
            )
            @inject_services('health_monitor')
            def update_health_status(n_intervals: int, health_monitor: Any) -> Any:
                """Update system health status"""
                try:
                    if health_monitor is not None:
                        health_status = health_monitor.get_health_status()
                        
                        # Create health indicator
                        if health_status.get('database', {}).get('status') == 'healthy':
                            return dbc.Badge("🟢 System Healthy", color="success", className="me-2")
                        else:
                            return dbc.Badge("🔴 System Issues", color="danger", className="me-2")
                    else:
                        return dbc.Badge("⚪ Health Unknown", color="secondary", className="me-2")
                
                except Exception as e:
                    logger.error(f"Error updating health status: {e}")
                    return dbc.Badge("❌ Health Error", color="danger", className="me-2")
        
        except ImportError:
            logger.warning("Could not register health callbacks - Dash components not available")
    
    def _register_analytics_callbacks(self) -> None:
        """Enhanced analytics callback registration"""
        analytics_module = self.registry.get_component('analytics_module')
        if analytics_module is not None:
            register_func = getattr(analytics_module, 'register_analytics_callbacks', None)
            if register_func is not None:
                try:
                    # Always pass container for DI
                    register_func(self.app, self.container)
                    logger.info("Analytics callbacks registered with DI container")
                except Exception as e:
                    logger.error(f"Error registering analytics callbacks: {e}")
    
    def _register_page_routing_callback(self) -> None:
        """Enhanced page routing with service injection"""
        try:
            from dash import Output, Input
            
            @self.app.callback(
                Output('page-content', 'children'),
                Input('url', 'pathname'),
                prevent_initial_call=False
            )
            @inject_services('config')
            def display_page(pathname: Optional[str], config: Any) -> Any:
                """Route to appropriate page with service injection"""
                try:
                    if pathname == '/analytics':
                        return self._handle_analytics_page()
                    elif pathname == '/health':
                        return self._handle_health_page()
                    else:
                        return self.layout_manager.create_dashboard_content()
                        
                except Exception as e:
                    logger.error(f"Error in page routing: {e}")
                    return self._create_error_page(f"Page routing error: {str(e)}")
        
        except ImportError:
            logger.error("Cannot register page routing - Dash not available")
    
    def _handle_health_page(self) -> Any:
        """Handle system health page"""
        try:
            from dash import html
            import dash_bootstrap_components as dbc
            
            # Get health status from container
            health_status = self.container.health_check()
            
            return dbc.Container([
                html.H1("🏥 System Health", className="text-primary mb-4"),
                
                dbc.Card([
                    dbc.CardHeader("Container Status"),
                    dbc.CardBody([
                        html.P(f"Status: {health_status['status']}"),
                        html.P(f"Services Registered: {health_status['services_registered']}"),
                        html.P(f"Instances Created: {health_status['instances_created']}"),
                        html.P(f"Container Started: {health_status['started']}"),
                    ])
                ], className="mb-4"),
                
                dbc.Card([
                    dbc.CardHeader("Service Health"),
                    dbc.CardBody([
                        html.P(f"Config Service: {'✅' if health_status['key_services']['config'] else '❌'}"),
                        html.P(f"Database Service: {'✅' if health_status['key_services']['database'] else '❌'}"),
                    ])
                ])
            ], fluid=True, className="p-4")
            
        except Exception as e:
            logger.error(f"Error creating health page: {e}")
            return self._create_error_page(f"Health page error: {str(e)}")
    
    # ... (other existing methods remain the same)
    
    def _handle_analytics_page(self) -> Any:
        """Handle analytics page"""
        analytics_module = self.registry.get_component('analytics_module')
        
        if analytics_module is not None:
            layout_func = getattr(analytics_module, 'layout', None)
            if layout_func is not None and callable(layout_func):
                try:
                    return layout_func()
                except Exception as e:
                    logger.error(f"Error creating analytics layout: {e}")
                    return self._create_error_page(f"Error loading analytics page: {str(e)}")
        
        return self._create_error_page("Analytics page not available")
    
    def _create_error_page(self, message: str) -> Any:
        """Create error page"""
        try:
            from dash import html
            import dash_bootstrap_components as dbc
            
            return html.Div([
                dbc.Alert(message, color="warning", className="m-3")
            ])
        except ImportError:
            return None
    
    def _register_component_callbacks(self) -> None:
        """Register component callbacks"""
        map_panel_register = self.registry.get_component('map_panel_callbacks')
        if map_panel_register is not None:
            try:
                map_panel_register(self.app)
                logger.info("Map panel callbacks registered")
            except Exception as e:
                logger.error(f"Error registering map panel callbacks: {e}")
    
    def _register_navbar_callback(self) -> None:
        """Register navbar callback"""
        try:
            from dash import Output, Input
            from datetime import datetime
            
            @self.app.callback(
                Output("live-time", "children"),
                Input("live-time", "id"),
                prevent_initial_call=False
            )
            def update_time(_: Any) -> str:
                """Update live time display"""
                try:
                    return f"Live Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                except Exception as e:
                    logger.error(f"Error updating time: {e}")
                    return "Time unavailable"
        
        except Exception as e:
            logger.error(f"Error registering navbar callback: {e}")

# ============================================================================
# Usage example - tests/test_di_integration.py
"""
Integration tests for the complete DI system
"""

def test_complete_di_integration():
    """Test the complete DI integration"""
    from core.app_factory import create_application
    from tests.test_di_container import DITestUtilities
    
    # Create test container
    test_container = DITestUtilities.create_test_container()
    
    with test_container.test_scope():
        # Create app with test container
        app = create_application()
        
        if app is not None:
            # Test service access
            config = app.get_service_optional('config')
            assert config is not None
            
            # Test health check
            health = app.container_health()
            assert health['status'] == 'healthy'
            
            print("✅ Complete DI integration test passed!")
        else:
            print("❌ Could not create application")

def run_all_di_tests():
    """Run all DI-related tests"""
    import unittest
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContainer))
    suite.addTest(unittest.makeSuite(TestServiceRegistry))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run integration test
    test_complete_di_integration()
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🧪 Running DI System Tests...")
    print("=" * 50)
    
    success = run_all_di_tests()
    
    if success:
        print("\n🎉 All DI tests passed!")
        print("Your Dependency Injection system is working correctly!")
    else:
        print("\n❌ Some DI tests failed. Check the output above.")