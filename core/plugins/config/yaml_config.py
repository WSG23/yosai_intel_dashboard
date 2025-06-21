"""Enhanced YAML configuration with validation and type safety"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import yaml
import os
from pathlib import Path
import logging

from core.exceptions import ConfigurationError
from .interfaces import IConfigurationManager

@dataclass
class DatabaseConfig:
    """Database configuration with validation"""
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    database: str = "yosai"
    type: str = "postgresql"

    def __post_init__(self) -> None:
        if self.type not in ["postgresql", "sqlite", "mock"]:
            raise ConfigurationError(f"Invalid database type: {self.type}")
        if self.type == "postgresql" and not self.password:
            logging.warning(
                "PostgreSQL password not set - using environment variable"
            )

@dataclass
class CacheConfig:
    """Cache configuration"""
    type: str = "memory"
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    timeout_seconds: int = 300
    max_memory_mb: int = 100
    key_prefix: str = "yosai:"

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = ""
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""
    session_timeout: int = 3600

    def __post_init__(self) -> None:
        if not self.secret_key:
            self.secret_key = os.urandom(32).hex()
            logging.warning(
                "Generated random secret key - set SECRET_KEY for production"
            )

@dataclass
class AppConfig:
    """Application configuration"""
    title: str = "Yōsai Intel Dashboard"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8050
    timezone: str = "UTC"
    language: str = "en"
    max_upload_size: int = 16 * 1024 * 1024

@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    cache_timeout_seconds: int = 300
    max_records_per_query: int = 10000
    enable_real_time: bool = True
    batch_size: int = 1000
    anomaly_detection_enabled: bool = True
    ml_models_path: str = "models/ml"

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    health_check_interval_seconds: int = 30
    performance_monitoring: bool = False
    error_reporting_enabled: bool = False
    sentry_dsn: Optional[str] = None

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "standard"
    file_path: str = "logs/app.log"
    max_file_size: int = 10 * 1024 * 1024
    backup_count: int = 5

@dataclass
class Configuration:
    """Main configuration container"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    app: AppConfig = field(default_factory=AppConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Configuration":
        """Load configuration from YAML file"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls(
                database=DatabaseConfig(**data.get("database", {})),
                cache=CacheConfig(**data.get("cache", {})),
                security=SecurityConfig(**data.get("security", {})),
                app=AppConfig(**data.get("app", {})),
                analytics=AnalyticsConfig(**data.get("analytics", {})),
                monitoring=MonitoringConfig(**data.get("monitoring", {})),
                logging=LoggingConfig(**data.get("logging", {})),
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration from {config_path}: {e}"
            )

    def apply_environment_overrides(self) -> None:
        """Apply environment variable overrides"""
        env_mappings = {
            "DB_HOST": ("database", "host"),
            "DB_PORT": ("database", "port"),
            "DB_USER": ("database", "username"),
            "DB_PASSWORD": ("database", "password"),
            "DB_NAME": ("database", "database"),
            "DB_TYPE": ("database", "type"),
            "SECRET_KEY": ("security", "secret_key"),
            "AUTH0_DOMAIN": ("security", "auth0_domain"),
            "AUTH0_CLIENT_ID": ("security", "auth0_client_id"),
            "AUTH0_CLIENT_SECRET": ("security", "auth0_client_secret"),
            "DEBUG": ("app", "debug"),
            "HOST": ("app", "host"),
            "PORT": ("app", "port"),
        }
        for env_var, (section, field_name) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                section_obj = getattr(self, section)
                field_type = type(getattr(section_obj, field_name))
                if field_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif field_type == int:
                    value = int(value)
                setattr(section_obj, field_name, value)

class ConfigurationManager(IConfigurationManager):
    """Configuration manager using YAML files"""
    def __init__(self) -> None:
        self.database_config = DatabaseConfig()
        self.cache_config = CacheConfig()
        self.app_config = AppConfig()
        self.security_config = SecurityConfig()
        self.analytics_config = AnalyticsConfig()
        self.monitoring_config = MonitoringConfig()
        self.logging_config = LoggingConfig()

    def load_configuration(self, config_path: Optional[str] = None) -> None:
        if config_path and Path(config_path).exists():
            config = Configuration.from_yaml(Path(config_path))
        else:
            config = Configuration()
        config.apply_environment_overrides()
        self.database_config = config.database
        self.cache_config = config.cache
        self.app_config = config.app
        self.security_config = config.security
        self.analytics_config = config.analytics
        self.monitoring_config = config.monitoring
        self.logging_config = config.logging

    def get_database_config(self) -> Any:
        """Get database configuration"""
        return self.database_config

    def get_cache_config(self) -> Any:
        """Get cache configuration"""
        return self.cache_config

    def get_app_config(self) -> Any:
        """Get app configuration"""
        return self.app_config

# Global singleton
_configuration_manager: Optional[ConfigurationManager] = None

def get_configuration_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _configuration_manager
    if _configuration_manager is None:
        _configuration_manager = ConfigurationManager()
    return _configuration_manager

__all__ = [
    "ConfigurationManager",
    "get_configuration_manager",
    "AppConfig",
    "DatabaseConfig",
    "CacheConfig",
    "SecurityConfig",
    "AnalyticsConfig",
    "MonitoringConfig",
    "LoggingConfig",
    "Configuration",
    "ConfigurationError",
]
