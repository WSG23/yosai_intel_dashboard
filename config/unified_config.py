"""
Unified Configuration Management for Yōsai Intel Dashboard
Replaces multiple configuration systems with single source of truth
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UnifiedConfigManager:
    """Single configuration manager for all environments"""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self._load_configuration()

    def _load_configuration(self):
        """Load configuration with environment precedence"""
        # Determine environment
        env = os.getenv('YOSAI_ENV', 'development')

        # Load base configuration
        config_file = f"config/{env}.yaml"
        config_path = Path(config_file)

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Fallback to default config
            self.config = self._get_default_config()

        # Override with environment variables
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            'DB_HOST': 'database.host',
            'DB_PORT': 'database.port',
            'DB_NAME': 'database.database',
            'DB_USER': 'database.username',
            'DB_PASSWORD': 'database.password',
            'SECRET_KEY': 'security.secret_key',
            'HOST': 'app.host',
            'PORT': 'app.port',
            'DEBUG': 'app.debug'
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value)

    def _set_nested_value(self, path: str, value: str):
        """Set nested configuration value from dot notation"""
        keys = path.split('.')
        current = self.config

        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        # Convert string values to appropriate types
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in ('true', 'false'):
                value = lowered == 'true'
            elif value.isdigit():
                value = int(value)
        current[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        current = self.config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration fallback"""
        return {
            'app': {
                'debug': True,
                'host': '127.0.0.1',
                'port': 8050,
                'title': 'Yōsai Intel Dashboard'
            },
            'database': {
                'type': 'mock',
                'host': 'localhost',
                'port': 5432
            },
            'security': {
                'secret_key': os.getenv('SECRET_KEY', 'change-me-in-production')
            }
        }


# Singleton instance
_config_manager: Optional[UnifiedConfigManager] = None


def get_config() -> UnifiedConfigManager:
    """Get singleton configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = UnifiedConfigManager()
    return _config_manager

__all__ = ["UnifiedConfigManager", "get_config"]
