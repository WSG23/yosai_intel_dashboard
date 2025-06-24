"""Minimal plugin config compatibility"""

# Re-export from main config to prevent import errors
try:
    from config.config_manager import (
        ConfigManager,
        get_config,
        AppConfig,
        DatabaseConfig,
    )
    from config.cache_manager import CacheConfig

    # Service locator compatibility
    def get_service_locator():
        """Compatibility function for service locator"""
        return get_config()

    __all__ = [
        'ConfigManager',
        'get_config',
        'get_service_locator',
        'AppConfig',
        'DatabaseConfig',
        'CacheConfig',
    ]

except ImportError:
    # Minimal fallback if main config not available
    def get_service_locator():
        return None

    __all__ = ['get_service_locator']
