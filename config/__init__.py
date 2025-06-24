"""Simplified configuration package without plugin indirection."""

from .config_manager import (
    ConfigManager,
    get_config,
    DatabaseConfig,
    AppConfig,
)
from .cache_manager import CacheConfig

from .database_manager import (
    DatabaseManager,
    MockDatabaseConnection,
)

from .cache_manager import MemoryCacheManager, RedisCacheManager

__all__ = [
    'ConfigManager',
    'get_config',
    'AppConfig',
    'DatabaseConfig',
    'CacheConfig',
    'DatabaseManager',
    'MockDatabaseConnection',
    'MemoryCacheManager',
    'RedisCacheManager',
]
