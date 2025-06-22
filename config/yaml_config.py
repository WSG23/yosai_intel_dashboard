"""Unified YAML Configuration Management System"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Application configuration with validation"""
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8050
    title: str = "Yōsai Intel Dashboard"
    timezone: str = "UTC"
    log_level: str = "INFO"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "mock"
    host: str = "localhost"
    port: int = 5432
    database: str = "yosai_intel"
    username: str = "postgres"
    password: str = ""

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = "dev-key-change-in-production"
    session_timeout_minutes: int = 60
    max_file_size_mb: int = 100

class ConfigurationManager:
    """Main configuration manager - single source of truth"""

    def __init__(self) -> None:
        self.app_config = AppConfig()
        self.database_config = DatabaseConfig()
        self.security_config = SecurityConfig()
        self._loaded_files: List[str] = []

    def load_configuration(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML file with environment overrides"""
        if not config_path:
            env = os.getenv("YOSAI_ENV", "development")
            config_path = f"config/{env}.yaml"

        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            if "app" in data:
                self.app_config = AppConfig(**data["app"])
            if "database" in data:
                self.database_config = DatabaseConfig(**data["database"])
            if "security" in data:
                self.security_config = SecurityConfig(**data["security"])
            self._loaded_files.append(config_path)

        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        env_mappings = {
            "DB_HOST": ("database_config", "host"),
            "DB_PORT": ("database_config", "port"),
            "DB_USER": ("database_config", "username"),
            "DB_PASSWORD": ("database_config", "password"),
            "SECRET_KEY": ("security_config", "secret_key"),
            "DEBUG": ("app_config", "debug"),
            "HOST": ("app_config", "host"),
            "PORT": ("app_config", "port"),
        }

        for env_var, (obj_name, field) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                obj = getattr(self, obj_name)
                current_type = type(getattr(obj, field))
                if current_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif current_type == int:
                    value = int(value)
                setattr(obj, field, value)

_config_manager: Optional[ConfigurationManager] = None

def get_configuration_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
        _config_manager.load_configuration()
    return _config_manager
