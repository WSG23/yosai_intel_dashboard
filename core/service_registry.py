# core/service_registry.py
"""Service registry - configures all your existing services with DI"""
from typing import Any
import logging
from .container import Container, get_container
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

def configure_container(container: Container) -> None:
    """Configure the container with all your existing services"""
    
    # 1. CONFIGURATION (Foundation)
    container.register(
        'config',
        lambda: ConfigManager.from_environment(),
        singleton=True
    )
    
    # 2. DATABASE (Depends on config)
    container.register(
        'database',
        create_database_connection,
        singleton=True,
        dependencies=['config']
    )
    
    # 3. MODELS (Depend on database)
    container.register(
        'access_model',
        create_access_model,
        singleton=True,
        dependencies=['database']
    )
    
    container.register(
        'anomaly_model', 
        create_anomaly_model,
        singleton=True,
        dependencies=['database']
    )
    
    # 4. SERVICES (Depend on models and config)
    container.register(
        'analytics_service',
        create_analytics_service,
        singleton=True,
        dependencies=['access_model', 'anomaly_model', 'config']
    )
    
    container.register(
        'file_processor',
        create_file_processor,
        singleton=True,
        dependencies=['config']
    )
    
    # 5. UTILITY SERVICES
    container.register(
        'cache_manager',
        create_cache_manager,
        singleton=True,
        dependencies=['config']
    )
    
    logger.info("Container configured with all services")

# Factory functions for your existing services
def create_database_connection(config: ConfigManager) -> Any:
    """Create database connection using your existing DatabaseManager"""
    try:
        from config.database_manager import DatabaseManager
        
        # Create database config from your existing ConfigManager
        db_config = DatabaseManager.from_environment()
        return DatabaseManager.create_connection(db_config)
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        # Return mock database as fallback
        from config.database_manager import MockDatabaseConnection
        return MockDatabaseConnection()

def create_access_model(database: Any) -> Any:
    """Create access model using your existing factory"""
    try:
        from models.access_events import create_access_event_model
        return create_access_event_model(database)
    except Exception as e:
        logger.error(f"Failed to create access model: {e}")
        return None

def create_anomaly_model(database: Any) -> Any:
    """Create anomaly model using your existing ModelFactory"""
    try:
        from models.base import ModelFactory
        return ModelFactory.create_anomaly_model(database)
    except Exception as e:
        logger.error(f"Failed to create anomaly model: {e}")
        return None

def create_analytics_service(access_model: Any, anomaly_model: Any, config: ConfigManager) -> Any:
    """Create analytics service using your existing class"""
    try:
        from services.analytics_service import AnalyticsService
        
        # Create with your existing AnalyticsConfig if it exists
        try:
            from services.analytics_service import AnalyticsConfig
            analytics_config = AnalyticsConfig(
                cache_timeout_seconds=300,
                max_records_per_query=10000
            )
            return AnalyticsService(analytics_config)
        except ImportError:
            # Fallback: use the service without config
            return AnalyticsService()
            
    except Exception as e:
        logger.error(f"Failed to create analytics service: {e}")
        return None

def create_file_processor(config: ConfigManager) -> Any:
    """Create file processor using your existing components"""
    try:
        from components.analytics.file_processing import FileProcessor
        return FileProcessor()
    except Exception as e:
        logger.error(f"Failed to create file processor: {e}")
        return None

def create_cache_manager(config: ConfigManager) -> Any:
    """Create a simple cache manager"""
    return SimpleCacheManager(config)

class SimpleCacheManager:
    """Simple cache manager for the dashboard"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._cache = {}
        self.timeout = 300  # 5 minutes default
    
    def get(self, key: str) -> Any:
        """Get from cache"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set cache value"""
        self._cache[key] = value
    
    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()
    
    async def preload_analytics_data(self) -> None:
        """Preload analytics data"""
        logger.info("Preloading analytics data...")
    
    async def preload_dashboard_data(self) -> None:
        """Preload dashboard data"""
        logger.info("Preloading dashboard data...")

def create_configured_container() -> Container:
    """Create and configure a container with all services"""
    container = Container()
    configure_container(container)
    return container

def get_configured_container() -> Container:
    """Get the global configured container"""
    container = get_container()
    
    # Configure if not already configured
    if not container.has('config'):
        configure_container(container)
    
    return container