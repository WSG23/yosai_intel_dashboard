"""Enhanced YAML configuration with validation and type safety"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import yaml
import os
from pathlib import Path
import logging

from core.exceptions import ConfigurationError


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
    security: SecurityConfig = field(default_factory=SecurityConfig)
    app: AppConfig = field(default_factory=AppConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Configuration":
        """Load configuration from YAML file"""

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)

            return cls(
                database=DatabaseConfig(**data.get("database", {})),
                security=SecurityConfig(**data.get("security", {})),
                app=AppConfig(**data.get("app", {})),
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

