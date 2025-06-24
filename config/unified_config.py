from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
import yaml
import logging

@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "yosai.db"
    user: str = "user"
    password: str = ""

    def get_connection_string(self) -> str:
        if self.type == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.type == "sqlite":
            return f"sqlite:///{self.name}"
        else:
            return f"mock://{self.name}"

@dataclass
class AppConfig:
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8050
    secret_key: str = "dev-key-change-in-production"
    environment: str = "development"

@dataclass
class PluginConfig:
    """Configuration for plugins"""
    enabled_plugins: List[str] = field(default_factory=list)
    ai_classification: Dict[str, Any] = field(default_factory=dict)
    csrf_protection: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UnifiedConfig:
    """Single source of truth for all configuration"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    app: AppConfig = field(default_factory=AppConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)

    def validate(self) -> List[str]:
        """Validate configuration and return errors"""
        errors = []

        if self.app.environment == "production":
            if self.app.secret_key == "dev-key-change-in-production":
                errors.append("Production requires secure SECRET_KEY")
            if not self.database.password and self.database.type != "sqlite":
                errors.append("Production database requires password")

        return errors

class ConfigurationLoader:
    """Loads and merges configuration from multiple sources"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)

    def load_config(self, environment: Optional[str] = None) -> UnifiedConfig:
        """Load configuration with environment precedence"""
        environment = environment or os.getenv("YOSAI_ENV", "development")

        # Load base configuration
        config_data = self._load_yaml_files(environment)

        # Apply environment overrides
        config_data = self._apply_env_overrides(config_data)

        # Create configuration objects
        return self._build_config(config_data)

    def _load_yaml_files(self, environment: str) -> Dict[str, Any]:
        """Load YAML configuration files"""
        config_data = {}

        # Load base config
        base_file = self.config_dir / "config.yaml"
        if base_file.exists():
            with open(base_file, 'r') as f:
                config_data.update(yaml.safe_load(f) or {})

        # Load environment-specific config
        env_file = self.config_dir / f"{environment}.yaml"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                config_data.update(env_config)

        return config_data

    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_mappings = {
            'DB_TYPE': 'database.type',
            'DB_HOST': 'database.host',
            'DB_PORT': 'database.port',
            'DB_NAME': 'database.name',
            'DB_USER': 'database.user',
            'DB_PASSWORD': 'database.password',
            'DEBUG': 'app.debug',
            'HOST': 'app.host',
            'PORT': 'app.port',
            'SECRET_KEY': 'app.secret_key',
        }

        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                self._set_nested_value(config_data, config_path, os.environ[env_var])

        return config_data

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: str) -> None:
        """Set nested dictionary value using dot notation"""
        keys = path.split('.')
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Type conversion
        final_key = keys[-1]
        if final_key in ['port', 'debug']:
            try:
                current[final_key] = int(value) if final_key == 'port' else value.lower() == 'true'
            except ValueError:
                current[final_key] = value
        else:
            current[final_key] = value

    def _build_config(self, config_data: Dict[str, Any]) -> UnifiedConfig:
        """Build configuration objects from data"""
        db_data = config_data.get('database', {})
        app_data = config_data.get('app', {})
        plugin_data = config_data.get('plugins', {})

        return UnifiedConfig(
            database=DatabaseConfig(**db_data),
            app=AppConfig(**app_data),
            plugins=PluginConfig(**plugin_data)
        )

# Global configuration instance
_config: Optional[UnifiedConfig] = None
_loader: Optional[ConfigurationLoader] = None


def get_config() -> UnifiedConfig:
    """Get global configuration instance"""
    global _config, _loader
    if _config is None:
        _loader = ConfigurationLoader()
        _config = _loader.load_config()

        # Validate configuration
        errors = _config.validate()
        if errors:
            raise ValueError(f"Configuration errors: {errors}")

    return _config


def reload_config() -> UnifiedConfig:
    """Reload configuration (useful for testing)"""
    global _config
    _config = None
    return get_config()
