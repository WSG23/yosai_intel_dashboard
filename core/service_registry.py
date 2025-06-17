# core/service_registry.py
"""
Fixed Service Registry with Layered Architecture
Prevents circular dependencies by organizing services into layers
"""
from typing import Any, Optional
import logging
from .di_container import DIContainer, ServiceScope, ServiceLayer, get_container

logger = logging.getLogger(__name__)

def configure_container() -> DIContainer:
    """Configure the container with all services in proper layer order"""
    container = get_container()
    
    # Clear any existing configuration
    container.clear()
    
    print("🔧 Configuring DI Container with Layered Architecture...")
    
    # ========================================================================
    # LAYER 0: FOUNDATION - Configuration, logging, basic infrastructure
    # ========================================================================
    print("   📦 Layer 0: Foundation services...")
    
    # Configuration Manager (no dependencies)
    container.register(
        'config_manager',
        create_config_manager,
        scope=ServiceScope.SINGLETON,
        layer=ServiceLayer.FOUNDATION,
        tags={'core', 'config'}
    )
    
    # Individual config sections (depend only on config_manager)
    config_sections = ['app_config', 'database_config', 'cache_config', 
                      'security_config', 'analytics_config', 'monitoring_config']
    
    for section in config_sections:
        container.register(
            section,
            lambda config_manager, section=section: getattr(config_manager, section),
            scope=ServiceScope.SINGLETON,
            dependencies=['config_manager'],
            layer=ServiceLayer.FOUNDATION,
            tags={'config', 'foundation'}
        )
    
    # ========================================================================
    # LAYER 1: INFRASTRUCTURE - Database, cache, external connections
    # ========================================================================
    print("   🏗️ Layer 1: Infrastructure services...")
    
    # Database (depends only on database_config)
    container.register(
        'database',
        create_database_connection,
        scope=ServiceScope.SINGLETON,
        dependencies=['database_config'],
        layer=ServiceLayer.INFRASTRUCTURE,
        tags={'infrastructure', 'database'}
    )
    
    # Cache Manager (depends only on cache_config)
    container.register(
        'cache_manager',
        create_cache_manager,
        scope=ServiceScope.SINGLETON,
        dependencies=['cache_config'],
        layer=ServiceLayer.INFRASTRUCTURE,
        tags={'infrastructure', 'cache'}
    )
    
    # ========================================================================
    # LAYER 2: MODELS - Data models and repositories
    # ========================================================================
    print("   📊 Layer 2: Data models...")
    
    # Access Model (depends only on database)
    container.register(
        'access_model',
        create_access_model,
        scope=ServiceScope.SINGLETON,
        dependencies=['database'],
        layer=ServiceLayer.MODELS,
        tags={'model', 'data'}
    )
    
    # Anomaly Model (depends only on database)
    container.register(
        'anomaly_model',
        create_anomaly_model,
        scope=ServiceScope.SINGLETON,
        dependencies=['database'],
        layer=ServiceLayer.MODELS,
        tags={'model', 'data', 'ml'}
    )
    
    # ========================================================================
    # LAYER 3: SERVICES - Business logic services
    # ========================================================================
    print("   ⚙️ Layer 3: Business services...")
    
    # Analytics Service (depends on models and config)
    container.register(
        'analytics_service',
        create_analytics_service,
        scope=ServiceScope.SINGLETON,
        dependencies=['access_model', 'anomaly_model', 'analytics_config'],
        layer=ServiceLayer.SERVICES,
        tags={'service', 'analytics', 'business'}
    )
    
    # File Processor (depends only on security_config)
    container.register(
        'file_processor',
        create_file_processor,
        scope=ServiceScope.SINGLETON,
        dependencies=['security_config'],
        layer=ServiceLayer.SERVICES,
        tags={'service', 'file', 'security'}
    )
    
    # ========================================================================
    # LAYER 4: CONTROLLERS - Web controllers, APIs (if needed)
    # ========================================================================
    print("   🌐 Layer 4: Controllers...")
    
    # API Controller (depends on services)
    container.register(
        'api_controller',
        create_api_controller,
        scope=ServiceScope.SINGLETON,
        dependencies=['analytics_service', 'file_processor'],
        layer=ServiceLayer.CONTROLLERS,
        tags={'controller', 'api', 'web'}
    )
    
    # ========================================================================
    # LAYER 5: MONITORING - Health checks, metrics (top layer)
    # ========================================================================
    print("   📈 Layer 5: Monitoring services...")
    
    # Health Monitor (depends on infrastructure services for monitoring)
    container.register(
        'health_monitor',
        create_health_monitor,
        scope=ServiceScope.SINGLETON,
        dependencies=['database', 'cache_manager', 'monitoring_config'],
        layer=ServiceLayer.MONITORING,
        tags={'monitoring', 'health', 'diagnostics'}
    )
    
    print("✅ Container configuration complete!")
    logger.info("DI Container configured with layered architecture")
    
    return container

# ============================================================================
# FACTORY FUNCTIONS - Clean, testable, modular implementations
# ============================================================================

def create_config_manager() -> Any:
    """Create configuration manager"""
    try:
        from config.yaml_config import ConfigurationManager
        return ConfigurationManager.from_environment()
    except ImportError as e:
        logger.warning(f"YAML config not available: {e}")
        from core.config_manager import ConfigManager
        return ConfigManager.from_environment()

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
        from config.database_manager import MockDatabaseConnection
        return MockDatabaseConnection()

def create_cache_manager(cache_config: Any) -> Any:
    """Create cache manager from config"""
    try:
        cache_type = getattr(cache_config, 'type', 'memory')
        
        if cache_type == 'redis':
            from config.cache_manager import RedisCacheManager
            return RedisCacheManager(cache_config)
        else:
            from config.cache_manager import MemoryCacheManager
            return MemoryCacheManager(cache_config)
            
    except Exception as e:
        logger.error(f"Failed to create cache manager: {e}")
        from config.cache_manager import NullCacheManager
        return NullCacheManager()

def create_access_model(database: Any) -> Any:
    """Create access model with database"""
    try:
        from models.access_model import AccessModel
        return AccessModel(database)
    except Exception as e:
        logger.error(f"Failed to create access model: {e}")
        from models.access_model import MockAccessModel
        return MockAccessModel()

def create_anomaly_model(database: Any) -> Any:
    """Create anomaly model with database"""
    try:
        from models.anomaly_model import AnomalyModel
        return AnomalyModel(database)
    except Exception as e:
        logger.error(f"Failed to create anomaly model: {e}")
        from models.anomaly_model import MockAnomalyModel
        return MockAnomalyModel()

def create_analytics_service(access_model: Any, anomaly_model: Any, analytics_config: Any) -> Any:
    """Create analytics service with dependencies"""
    try:
        from services.analytics_service import AnalyticsService, AnalyticsConfig
        
        # Create service config from YAML config
        service_config = AnalyticsConfig(
            default_time_range_days=30,
            max_records_per_query=getattr(analytics_config, 'max_records_per_query', 10000),
            cache_timeout_seconds=getattr(analytics_config, 'cache_timeout_seconds', 300),
            min_confidence_threshold=0.7
        )
        
        # NOTE: Cache is injected at service level, not constructor level
        # This prevents circular dependencies between cache and services
        service = AnalyticsService(service_config)
        service.set_models(access_model, anomaly_model)
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create analytics service: {e}")
        from services.analytics_service import MockAnalyticsService
        return MockAnalyticsService()

def create_file_processor(security_config: Any) -> Any:
    """Create file processor with security config"""
    try:
        from components.analytics.file_processing import FileProcessor
        
        # Configure file processor with security settings
        processor = FileProcessor()
        processor.configure_security(
            max_file_size=getattr(security_config, 'max_file_size_mb', 50) * 1024 * 1024,
            allowed_extensions=getattr(security_config, 'allowed_file_extensions', ['.csv', '.xlsx']),
            scan_for_malware=getattr(security_config, 'scan_for_malware', False)
        )
        
        return processor
        
    except Exception as e:
        logger.error(f"Failed to create file processor: {e}")
        from components.analytics.file_processing import MockFileProcessor
        return MockFileProcessor()

def create_api_controller(analytics_service: Any, file_processor: Any) -> Any:
    """Create API controller with services"""
    try:
        from controllers.api_controller import APIController
        return APIController(analytics_service, file_processor)
    except Exception as e:
        logger.error(f"Failed to create API controller: {e}")
        from controllers.api_controller import MockAPIController
        return MockAPIController()

def create_health_monitor(database: Any, cache_manager: Any, monitoring_config: Any) -> Any:
    """Create health monitor with infrastructure dependencies"""
    try:
        from monitoring.health_monitor import HealthMonitor
        
        monitor = HealthMonitor(monitoring_config)
        monitor.add_dependency('database', database)
        monitor.add_dependency('cache', cache_manager)
        
        return monitor
        
    except Exception as e:
        logger.error(f"Failed to create health monitor: {e}")
        from monitoring.health_monitor import MockHealthMonitor
        return MockHealthMonitor()

# ============================================================================
# ENHANCED CACHE INTEGRATION - Prevents circular dependencies
# ============================================================================

def enhance_services_with_cache(container: DIContainer) -> None:
    """Enhance services with cache after initial registration
    
    This function safely adds cache functionality to services without
    creating circular dependencies by using post-initialization injection.
    """
    try:
        cache_manager = container.get('cache_manager')
        analytics_service = container.get('analytics_service')
        
        # Inject cache into analytics service if it supports it
        if hasattr(analytics_service, 'set_cache'):
            analytics_service.set_cache(cache_manager)
            logger.info("Enhanced analytics service with cache")
            
    except Exception as e:
        logger.warning(f"Could not enhance services with cache: {e}")

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_configured_container() -> DIContainer:
    """Get a fully configured container"""
    container = configure_container()
    
    # Start lifecycle services in proper order
    container.start_lifecycle_services()
    
    # Add cache enhancement after basic setup
    enhance_services_with_cache(container)
    
    return container

def create_test_container() -> DIContainer:
    """Create a container configured for testing"""
    container = DIContainer("test")
    
    # Register minimal test services
    container.register('config_manager', lambda: create_mock_config(), layer=ServiceLayer.FOUNDATION)
    container.register('database', lambda: create_mock_database(), layer=ServiceLayer.INFRASTRUCTURE)
    
    return container
# Temporary function from create_yaml_config_files.py
def get_configured_container_with_yaml(config_manager: Optional[Any] = None) -> DIContainer:
    """Get container configured with YAML configuration"""
    return configure_container()