"""Simplified configuration package"""

from .config import (
    Config, AppConfig, DatabaseConfig, SecurityConfig,
    ConfigManager, get_config, reload_config,
    get_app_config, get_database_config, get_security_config,
)

from .database_manager import (
    DatabaseManager, MockConnection, DatabaseConfig as DBConfig,
    SQLiteConnection, DatabaseConnection
)

__all__ = [
    'Config', 'AppConfig', 'DatabaseConfig', 'SecurityConfig',
    'ConfigManager', 'get_config', 'reload_config',
    'get_app_config', 'get_database_config', 'get_security_config',
    'DatabaseManager', 'MockConnection', 'DBConfig',
    'SQLiteConnection', 'DatabaseConnection'
]
