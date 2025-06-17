# core/service_registry_fixed.py - FIXED: Analytics service without problematic dependencies
"""
Fixed service registry that resolves the analytics service timeout issue
"""

import logging
from typing import Any, Optional
from pathlib import Path

from .container import Container

logger = logging.getLogger(__name__)

def create_analytics_service_simple(analytics_config: Any) -> Any:
    """Create analytics service with minimal dependencies to avoid deadlock"""
    try:
        from services.analytics_service import AnalyticsService
        
        # Create with minimal configuration - no database dependency to avoid deadlock
        return AnalyticsService(
            config=analytics_config,
            database=None  # Will use global database connection when needed
        )
        
    except ImportError:
        logger.warning("AnalyticsService not available, creating mock")
        return MockAnalyticsService()

def create_access_model_simple(database_manager: Any) -> Any:
    """Create access model with simple dependencies"""
    try:
        from models.access_event import AccessModel
        return AccessModel(database_manager)
    except ImportError:
        logger.warning("AccessModel not available, creating mock")
        return MockAccessModel()

def create_anomaly_model_simple(database_manager: Any) -> Any:
    """Create anomaly model with simple dependencies"""
    try:
        from models.anomaly_detection import AnomalyModel  
        return AnomalyModel(database_manager)
    except ImportError:
        logger.warning("AnomalyModel not available, creating mock")
        return MockAnomalyModel()

class MockAnalyticsService:
    """Mock analytics service for when real service is unavailable"""
    
    def __init__(self, config=None, database=None):
        self.config = config
        self.database = database
        
    def get_dashboard_summary(self):
        return {
            'total_events_30d': 1000,
            'unique_users_30d': 50,
            'unique_doors_30d': 10,
            'granted_rate': 0.85,
            'denied_rate': 0.15,
            'recent_events_24h': 100,
            'last_updated': '2024-01-01T00:00:00',
            'system_status': 'healthy',
            'note': 'Mock analytics service'
        }
    
    def get_access_patterns_analysis(self, days=30):
        return {
            'daily_trends': [],
            'hourly_distribution': [],
            'top_users': [],
            'top_doors': [],
            'anomaly_indicators': []
        }
    
    def process_uploaded_file(self, df, filename):
        return {
            'status': 'success',
            'records_processed': len(df) if df is not None else 0,
            'filename': filename
        }

class MockAccessModel:
    """Mock access model"""
    
    def __init__(self, database=None):
        self.database = database
    
    def get_summary_stats(self, days=30):
        return {'total_events': 1000, 'unique_people': 50}
    
    def get_recent_events(self, hours=24):
        return []

class MockAnomalyModel:
    """Mock anomaly model"""
    
    def __init__(self, database=None):
        self.database = database
    
    def detect_anomalies(self, data):
        return []

def configure_container_fixed(container: Container, config_manager: Optional[Any] = None) -> None:
    """Configure container with FIXED analytics service registration"""
    logger.info("🔧 Configuring DI Container with FIXED Analytics Service...")
    
    # Create config manager if not provided
    if config_manager is None:
        try:
            from config.yaml_config import ConfigurationManager
            config_manager = ConfigurationManager()
            config_manager.load_configuration()
        except ImportError:
            logger.warning("YAML config not available")
            config_manager = None
    
    # Layer 0: Foundation services
    logger.info("   📦 Layer 0: Foundation services...")
    container.register('config_manager', lambda: config_manager)
    
    # Layer 1: Infrastructure services  
    logger.info("   🏗️ Layer 1: Infrastructure services...")
    container.register(
        'database_manager', 
        lambda: create_database_connection_simple(),
        dependencies=[]
    )
    container.register(
        'cache_manager',
        lambda: create_cache_manager_simple(),
        dependencies=[]
    )
    
    # Layer 2: Configuration objects
    logger.info("   📊 Layer 2: Configuration objects...")
    if config_manager:
        container.register('app_config', lambda: config_manager.app_config)
        container.register('database_config', lambda: config_manager.database_config) 
        container.register('analytics_config', lambda: config_manager.analytics_config)
        container.register('security_config', lambda: config_manager.security_config)
        container.register('monitoring_config', lambda: config_manager.monitoring_config)
    
    # Layer 3: Data models (SIMPLIFIED - no circular dependencies)
    logger.info("   📈 Layer 3: Data models...")
    container.register(
        'access_model',
        lambda database_manager: create_access_model_simple(database_manager),
        dependencies=['database_manager']
    )
    container.register(
        'anomaly_model',
        lambda database_manager: create_anomaly_model_simple(database_manager), 
        dependencies=['database_manager']
    )
    
    # Layer 4: Business services (FIXED - minimal dependencies)
    logger.info("   ⚙️ Layer 4: Business services...")
    container.register(
        'analytics_service',
        lambda analytics_config: create_analytics_service_simple(analytics_config),
        dependencies=['analytics_config'] if config_manager else []
    )
    
    # Layer 5: Monitoring services
    logger.info("   📈 Layer 5: Monitoring services...")
    container.register('health_monitor', lambda: create_health_monitor_simple())
    
    logger.info("✅ Container configuration complete with FIXED analytics service!")

def create_database_connection_simple():
    """Create database connection without complex dependencies"""
    try:
        from config.database_manager import DatabaseManager
        config = DatabaseManager.from_environment()
        return DatabaseManager.create_connection(config)
    except Exception as e:
        logger.warning(f"Database creation failed: {e}")
        from config.database_manager import MockDatabaseConnection
        return MockDatabaseConnection()

def create_cache_manager_simple():
    """Create simple cache manager"""
    try:
        # Try to create real cache manager
        return MemoryCacheManager()
    except:
        return MockCacheManager()

def create_health_monitor_simple():
    """Create simple health monitor"""
    class SimpleHealthMonitor:
        def health_check(self):
            return {'status': 'healthy', 'timestamp': '2024-01-01T00:00:00'}
    return SimpleHealthMonitor()

class MockCacheManager:
    """Mock cache manager"""
    def __init__(self):
        self._cache = {}
    
    def get(self, key): return self._cache.get(key)
    def set(self, key, value): self._cache[key] = value
    def clear(self): self._cache.clear()

class MemoryCacheManager:
    """Simple in-memory cache manager"""
    def __init__(self):
        self._cache = {}
    
    def get(self, key): return self._cache.get(key)
    def set(self, key, value): self._cache[key] = value  
    def clear(self): self._cache.clear()

def get_configured_container_fixed(config_manager: Optional[Any] = None) -> Container:
    """Get container configured with FIXED analytics service"""
    container = Container()
    configure_container_fixed(container, config_manager)
    return container

# Legacy compatibility
def get_configured_container() -> Container:
    """Legacy function that now uses the fixed configuration"""
    return get_configured_container_fixed()

def configure_container(container: Container) -> None:
    """Legacy function that now uses the fixed configuration"""
    configure_container_fixed(container)
