"""Simplified configuration management system"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from core.exceptions import ConfigurationError


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "yosai.db"
    user: str = "user"
    password: str = ""


@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8050
    secret_key: str = "dev-key-change-in-production"
    environment: str = "development"


@dataclass
class Config:
    """Main configuration container"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    app: AppConfig = field(default_factory=AppConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.app.environment == "production":
            if self.app.secret_key == "dev-key-change-in-production":
                raise ConfigurationError("Production requires a secure SECRET_KEY")
            if not self.database.password:
                raise ConfigurationError("Production requires database password")


class ConfigManager:
    """Simplified configuration manager"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """Load configuration with environment overrides"""
        if self._config is None:
            self._config = self._build_config()
        return self._config
    
    def _build_config(self) -> Config:
        """Build configuration from YAML and environment"""
        # Load base config
        yaml_config = self._load_yaml_config()
        
        # Create config objects
        db_config = DatabaseConfig(
            type=self._get_env_or_yaml("DB_TYPE", yaml_config, "database.type", "sqlite"),
            host=self._get_env_or_yaml("DB_HOST", yaml_config, "database.host", "localhost"),
            port=int(self._get_env_or_yaml("DB_PORT", yaml_config, "database.port", 5432)),
            name=self._get_env_or_yaml("DB_NAME", yaml_config, "database.name", "yosai.db"),
            user=self._get_env_or_yaml("DB_USER", yaml_config, "database.user", "user"),
            password=self._get_env_or_yaml("DB_PASSWORD", yaml_config, "database.password", ""),
        )
        
        app_config = AppConfig(
            debug=self._get_env_bool("DEBUG", yaml_config, "app.debug", False),
            host=self._get_env_or_yaml("HOST", yaml_config, "app.host", "127.0.0.1"),
            port=int(self._get_env_or_yaml("PORT", yaml_config, "app.port", 8050)),
            secret_key=self._get_env_or_yaml("SECRET_KEY", yaml_config, "app.secret_key", "dev-key-change-in-production"),
            environment=self._get_env_or_yaml("YOSAI_ENV", yaml_config, "app.environment", "development"),
        )
        
        return Config(database=db_config, app=app_config)
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        config_file = self.config_dir / "config.yaml"
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML configuration: {e}")
    
    def _get_env_or_yaml(self, env_key: str, yaml_config: Dict, yaml_path: str, default: Any) -> Any:
        """Get value from environment or YAML config"""
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        return self._get_nested_value(yaml_config, yaml_path, default)
    
    def _get_env_bool(self, env_key: str, yaml_config: Dict, yaml_path: str, default: bool) -> bool:
        """Get boolean value from environment or YAML"""
        value = self._get_env_or_yaml(env_key, yaml_config, yaml_path, default)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def _get_nested_value(self, config: Dict, path: str, default: Any) -> Any:
        """Get nested value from config using dot notation"""
        keys = path.split('.')
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current


# Global config instance
config_manager = ConfigManager()
get_config = config_manager.load_config
