"""Enhanced modular configuration system"""

# Import interfaces
from .interfaces import (
    IDatabaseManager,
    ICacheManager,
    IConfigurationManager,
    ConnectionResult
)

# Import factories
from .factories import (
    DatabaseManagerFactory,
    CacheManagerFactory
)

# Import service locator
from .service_locator import (
    ConfigurationServiceLocator,
    get_service_locator
)

# Import concrete implementations
from .yaml_config import *
from .database_manager import (
    MockDatabaseManager,
    PostgreSQLDatabaseManager,
    SQLiteDatabaseManager
)
from .cache_manager import (
    MemoryCacheManager,
    RedisCacheManager,
    CacheEntry
)

# Export all public interfaces and classes
__all__ = [
    # Interfaces
    'IDatabaseManager',
    'ICacheManager',
    'IConfigurationManager',
    'ConnectionResult',

    # Factories
    'DatabaseManagerFactory',
    'CacheManagerFactory',

    # Service Locator
    'ConfigurationServiceLocator',
    'get_service_locator',

    # From yaml_config
    'ConfigurationManager',
    'get_configuration_manager',
    'AppConfig',
    'DatabaseConfig',
    'CacheConfig',
    'SecurityConfig',
    'AnalyticsConfig',
    'MonitoringConfig',
    'LoggingConfig',
    'Configuration',
    'ConfigurationError',

    # Database Managers
    'MockDatabaseManager',
    'PostgreSQLDatabaseManager',
    'SQLiteDatabaseManager',

    # Cache Managers
    'MemoryCacheManager',
    'RedisCacheManager',
    'CacheEntry'
]
