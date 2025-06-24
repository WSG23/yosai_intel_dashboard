"""Simplified configuration package without plugin indirection."""

from .yaml_config import (
    ConfigurationManager,
    get_configuration_manager,
    AppConfig,
    CacheConfig,
    SecurityConfig,
    AnalyticsConfig,
    MonitoringConfig,
    LoggingConfig,
)

from .database_manager import (
    DatabaseManager,
    MockConnection,  # Fixed: was MockDatabaseConnection
    DatabaseConfig,
    SQLiteConnection,
    DatabaseConnection,
)

try:
    from .cache_manager import MemoryCacheManager, RedisCacheManager
except ImportError:
    # Handle case where cache manager doesn't exist
    MemoryCacheManager = None
    RedisCacheManager = None

__all__ = [
    'ConfigurationManager',
    'get_configuration_manager', 
    'AppConfig',
    'DatabaseConfig',
    'CacheConfig',
    'DatabaseManager',
    'MockConnection',  # Fixed: was MockDatabaseConnection
    'SQLiteConnection',
    'DatabaseConnection',
    'MemoryCacheManager',
    'RedisCacheManager',
]
