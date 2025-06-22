# core/service_registry.py - FIXED: Updated to use proper ConfigurationManager methods
"""
Enhanced service registry with proper YAML configuration integration
Fixes the from_environment method issue
"""
import logging
from typing import Any, Optional, Dict
from pathlib import Path

from .container import Container

logger = logging.getLogger(__name__)

# ============================================================================
# FACTORY FUNCTIONS - Fixed and modular implementations
# ============================================================================

def create_config_manager() -> Any:
    """Create configuration manager - FIXED to use proper method"""
    try:
        # First try the YAML configuration with the proper from_environment method
        from config.yaml_config import ConfigurationManager
        return ConfigurationManager.from_environment()
    except ImportError as e:
        logger.warning(f"YAML config not available: {e}")
        try:
            # Fallback to other config manager if available
            from core.config_manager import ConfigManager
            return ConfigManager.from_environment()
        except ImportError as e2:
            logger.error(f"No configuration manager available: {e2}")
            # Create minimal config manager
            return MinimalConfigManager()

def create_database_connection(database_config: Any) -> Any:
    """Create database connection from config"""
    try:
        from config.database_manager import DatabaseManager, DatabaseConfig
        
        db_config = DatabaseConfig(
            db_type=database_config.type,
            host=database_config.host,
            port=database_config.port,
            database=database_config.database,
            username=database_config.username,
            password=database_config.password,
            pool_size=getattr(database_config, 'pool_size', 5)
        )
        
        return DatabaseManager.create_connection(db_config)
        
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        return MockDatabaseConnection()

def create_cache_manager(cache_config: Any) -> Any:
    """Create cache manager from config"""
    try:
        from config.cache_manager import CacheManager
        return CacheManager.from_config(cache_config)
    except Exception as e:
        logger.error(f"Failed to create cache manager: {e}")
        return MemoryCacheManager()

def create_error_handler() -> Any:
    """Create error handler"""
    try:
        from core.error_handling import ErrorHandler
        return ErrorHandler()
    except ImportError:
        return BasicErrorHandler()

def create_security_service(security_config: Any) -> Any:
    """Create security service"""
    try:
        from security.auth_service import SecurityService
        return SecurityService(security_config)
    except ImportError:
        return MockSecurityService()

def create_performance_monitor(monitoring_config: Any) -> Any:
    """Create performance monitor"""
    try:
        from monitoring.performance_monitor import PerformanceMonitor
        return PerformanceMonitor(monitoring_config)
    except ImportError:
        return MockPerformanceMonitor()

def create_analytics_service(analytics_config: Any, database: Any) -> Any:
    """Create analytics service"""
    try:
        from services.enhanced_analytics import EnhancedAnalyticsService
        return EnhancedAnalyticsService(analytics_config, database)
    except ImportError:
        return MockAnalyticsService()

# ============================================================================
# MOCK SERVICES - For testing and fallbacks
# ============================================================================

class MinimalConfigManager:
    """Minimal config manager for fallback"""
    def __init__(self):
        self.app_config = type('AppConfig', (), {
            'debug': False, 'host': '127.0.0.1', 'port': 8050
        })()
        self.database_config = type('DatabaseConfig', (), {
            'type': 'mock', 'host': 'localhost', 'port': 5432
        })()
        self.cache_config = type('CacheConfig', (), {
            'type': 'memory', 'host': 'localhost', 'port': 6379
        })()
        self.security_config = type('SecurityConfig', (), {
            'secret_key': 'fallback-key'
        })()
        self.analytics_config = type('AnalyticsConfig', (), {
            'enable_performance_tracking': True
        })()
        self.monitoring_config = type('MonitoringConfig', (), {
            'health_check_interval': 30
        })()

class MockDatabaseConnection:
    """Mock database for testing"""
    def query(self, sql): return []
    def execute(self, sql): return True
    def close(self): pass

class MemoryCacheManager:
    """Simple memory cache"""
    def __init__(self):
        self._cache = {}
    
    def get(self, key): return self._cache.get(key)
    def set(self, key, value): self._cache[key] = value
    def delete(self, key): self._cache.pop(key, None)
    def clear(self): self._cache.clear()

class BasicErrorHandler:
    """Basic error handler"""
    def handle_error(self, error, context):
        logger.error(f"Error in {context}: {error}")

class MockSecurityService:
    """Mock security service"""
    def validate_input(self, data): return True
    def authenticate(self, token): return True

class MockPerformanceMonitor:
    """Mock performance monitor"""
    def start_monitoring(self): pass
    def stop_monitoring(self): pass
    def get_metrics(self): return {}

class MockAnalyticsService:
    """Mock analytics service"""
    def get_dashboard_summary(self):
        return {'status': 'mock', 'total_events': 0}
    
    def process_uploaded_file(self, df, filename):
        return {'success': False, 'error': 'Mock service'}

class EnhancedHealthMonitor:
    """Enhanced health monitoring with detailed service checks"""
    
    def __init__(self, container: Container):
        self.container = container
        self.logger = logging.getLogger(__name__)
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'overall': 'healthy',
            'services': {},
            'container': {
                'registered_services': len(self.container._services),
                'service_names': list(self.container._services.keys())
            }
        }
        
        # Check individual services
        for service_name in self.container._services.keys():
            try:
                service = self.container.get_optional(service_name)
                if service is not None:
                    health_status['services'][service_name] = {
                        'status': 'healthy',
                        'type': type(service).__name__
                    }
                else:
                    health_status['services'][service_name] = {
                        'status': 'unavailable',
                        'type': 'None'
                    }
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                health_status['overall'] = 'degraded'
        
        return health_status

# ============================================================================
# CONTAINER CONFIGURATION FUNCTIONS
# ============================================================================

def configure_container_with_yaml(container: Container, config_manager: Optional[Any] = None) -> None:
    """Configure container with YAML configuration"""
    logger.info("🔧 Configuring DI Container with Layered Architecture...")
    
    # Create config manager if not provided
    if config_manager is None:
        config_manager = create_config_manager()
    
    # Layer 0: Foundation services
    logger.info("   📦 Layer 0: Foundation services...")
    container.register('config_manager', lambda: config_manager)
    container.register('error_handler', create_error_handler)
    
    # Layer 1: Infrastructure services  
    logger.info("   🏗️ Layer 1: Infrastructure services...")
    container.register(
        'database_manager', 
        lambda config_manager: create_database_connection(config_manager.database_config),
        dependencies=['config_manager']
    )
    container.register(
        'cache_manager',
        lambda config_manager: create_cache_manager(config_manager.cache_config),
        dependencies=['config_manager']
    )
    
    # Layer 2: Data models
    logger.info("   📊 Layer 2: Data models...")
    container.register('app_config', lambda config_manager: config_manager.app_config, dependencies=['config_manager'])
    container.register('database_config', lambda config_manager: config_manager.database_config, dependencies=['config_manager'])
    container.register('cache_config', lambda config_manager: config_manager.cache_config, dependencies=['config_manager'])
    container.register('security_config', lambda config_manager: config_manager.security_config, dependencies=['config_manager'])
    container.register('analytics_config', lambda config_manager: config_manager.analytics_config, dependencies=['config_manager'])
    container.register('monitoring_config', lambda config_manager: config_manager.monitoring_config, dependencies=['config_manager'])
    
    # Layer 3: Business services
    logger.info("   ⚙️ Layer 3: Business services...")
    container.register(
        'security_service',
        lambda security_config: create_security_service(security_config),
        dependencies=['security_config']
    )
    container.register(
        'analytics_service',
        lambda analytics_config, database_manager: create_analytics_service(analytics_config, database_manager),
        dependencies=['analytics_config', 'database_manager']
    )
    
    # Layer 4: Controllers 
    logger.info("   🌐 Layer 4: Controllers...")
    # Add controllers here when needed
    
    # Layer 5: Monitoring services
    logger.info("   📈 Layer 5: Monitoring services...")
    container.register(
        'performance_monitor',
        lambda monitoring_config: create_performance_monitor(monitoring_config),
        dependencies=['monitoring_config']
    )
    container.register('health_monitor', lambda: EnhancedHealthMonitor(container))
    
    logger.info("✅ Container configuration complete!")

def create_container_with_yaml(config_manager: Optional[Any] = None) -> Container:
    """Create container configured with YAML configuration"""
    container = Container()
    configure_container_with_yaml(container, config_manager)
    return container

# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

def configure_container(container: Container) -> None:
    """Legacy function for backward compatibility"""
    configure_container_with_yaml(container)

def get_configured_container() -> Container:
    """Legacy function for backward compatibility"""
    return get_configured_container_with_yaml()

def get_container() -> Container:
    """Get basic container instance"""
    return Container()

# ============================================================================
# TESTING AND VERIFICATION FUNCTIONS  
# ============================================================================

def test_container_configuration() -> Dict[str, Any]:
    """Test container configuration for troubleshooting"""
    try:
        # Test configuration manager creation
        config_manager = create_config_manager()
        
        # Test container configuration
        container = get_configured_container_with_yaml(config_manager)
        
        # Test health check
        health_monitor = container.get('health_monitor')
        health_status = health_monitor.health_check()
        
        return {
            'success': True,
            'config_manager_type': type(config_manager).__name__,
            'container_services': len(container._services),
            'health_status': health_status
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

def debug_configuration_loading() -> Dict[str, Any]:
    """Debug configuration loading process"""
    debug_info = {
        'config_files_found': [],
        'environment_vars': {},
        'import_status': {}
    }
    
    # Check for config files
    config_paths = [
        'config/config.yaml',
        'config/development.yaml', 
        'config/production.yaml',
        'config/test.yaml'
    ]
    
    for path in config_paths:
        if Path(path).exists():
            debug_info['config_files_found'].append(path)
    
    # Check environment variables
    env_vars = ['YOSAI_ENV', 'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY']
    for var in env_vars:
        debug_info['environment_vars'][var] = __import__('os').getenv(var, 'NOT_SET')
    
    # Check imports
    imports_to_test = [
        'config.yaml_config',
        'core.container',
        'core.error_handling'
    ]
    
    for import_name in imports_to_test:
        try:
            __import__(import_name)
            debug_info['import_status'][import_name] = 'SUCCESS'
        except Exception as e:
            debug_info['import_status'][import_name] = f'FAILED: {e}'
    
    return debug_info

# ============================================================================
# FIXED ANALYTICS SERVICE REGISTRATION
# ============================================================================

def get_configured_container_no_timeout(config_manager: Optional[Any] = None) -> Container:
    """Get container configured WITHOUT problematic analytics service dependencies"""
    from .service_registry_fixed import get_configured_container_fixed
    return get_configured_container_fixed(config_manager)

def configure_container_no_timeout(container: Container, config_manager: Optional[Any] = None) -> None:
    """Configure container WITHOUT problematic analytics service dependencies"""
    from .service_registry_fixed import configure_container_fixed
    configure_container_fixed(container, config_manager)

# Override the main functions to use fixed versions
def get_configured_container_with_yaml(config_manager: Optional[Any] = None) -> Container:
    """FIXED: Get container with working analytics service"""
    return get_configured_container_no_timeout(config_manager)
