"""Minimal plugin config compatibility"""

# Re-export from main config to prevent import errors
try:
    from config.yaml_config import (
        ConfigurationManager,
        get_configuration_manager,
        AppConfig,
        DatabaseConfig,
        CacheConfig,
        SecurityConfig
    )

    # Service locator compatibility
    def get_service_locator():
        """Compatibility function for service locator"""
        return get_configuration_manager()

    __all__ = [
        'ConfigurationManager',
        'get_configuration_manager',
        'get_service_locator',
        'AppConfig',
        'DatabaseConfig',
        'CacheConfig',
        'SecurityConfig'
    ]

except ImportError:
    # Minimal fallback if main config not available
    def get_service_locator():
        return None

    __all__ = ['get_service_locator']
