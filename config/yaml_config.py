"""YAML based configuration management for the dashboard."""

from __future__ import annotations

import os
import re
import yaml
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AppConfig:
    title: str = "Yosai Intelligence Dashboard"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8050
    log_level: str = "INFO"


@dataclass
class DatabaseConfig:
    type: str = "mock"
    host: str = "localhost"
    port: int = 5432
    name: str = "yosai_db"
    user: str = "yosai_user"
    password: str = ""


@dataclass
class CacheConfig:
    type: str = "memory"
    host: str = "localhost"
    port: int = 6379
    ttl: int = 300


@dataclass
class SecurityConfig:
    secret_key: str = "change-me"
    session_timeout: int = 3600
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)


@dataclass
class AnalyticsConfig:
    enabled: bool = True
    batch_size: int = 100
    max_records_per_query: int = 10000


@dataclass
class MonitoringConfig:
    health_check_interval: int = 30
    metrics_enabled: bool = True


@dataclass
class LoggingConfig:
    level: str = "INFO"


# ---------------------------------------------------------------------------
# Configuration Manager
# ---------------------------------------------------------------------------

class ConfigurationManager:
    """Load configuration from YAML files with env var overrides."""

    _env_pattern = re.compile(r"\$\{([^}]+)\}")

    def __init__(self) -> None:
        self.environment: str = os.getenv("YOSAI_ENV", "development")
        self._config_source: Optional[str] = None

        self.app_config = AppConfig()
        self.database_config = DatabaseConfig()
        self.cache_config = CacheConfig()
        self.security_config = SecurityConfig()
        self.analytics_config = AnalyticsConfig()
        self.monitoring_config = MonitoringConfig()
        self.logging_config = LoggingConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @classmethod
    def from_environment(cls) -> "ConfigurationManager":
        manager = cls()
        manager.load_configuration(None)
        return manager

    def load_configuration(self, file_path: Optional[str] = None) -> None:
        """Load configuration from YAML and apply environment overrides."""
        config_file = self._determine_config_file(file_path)
        self._config_source = str(config_file)

        data: Dict[str, Any] = {}
        if config_file and Path(config_file).exists():
            with open(config_file, "r", encoding="utf-8") as f:
                raw = f.read()
            substituted = self._substitute_env_vars(raw)
            data = yaml.safe_load(substituted) or {}

        self._apply_dict(data)
        self._apply_env_overrides()

    def get_app_config(self) -> AppConfig:
        return self.app_config

    def get_database_config(self) -> DatabaseConfig:
        return self.database_config

    def get_cache_config(self) -> CacheConfig:
        return self.cache_config

    def get_security_config(self) -> SecurityConfig:
        return self.security_config

    def validate_configuration(self) -> List[str]:
        """Return a list of configuration warnings."""
        warnings: List[str] = []

        if self.security_config.secret_key in {"change-me", "dev-key-change-in-production", "change-me-in-production"}:
            warnings.append("Secret key should be changed for production")

        if not self.app_config.debug and self.app_config.host == "127.0.0.1":
            warnings.append("Production app should not run on localhost")

        if self.database_config.type == "mock":
            warnings.append("Using mock database - not for production")

        if self.analytics_config.max_records_per_query > 50000:
            warnings.append("Analytics max_records_per_query too high")

        return warnings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _determine_config_file(self, path: Optional[str]) -> Path:
        if path:
            return Path(path)

        env_file = os.getenv("YOSAI_CONFIG_FILE")
        if env_file:
            return Path(env_file)

        env = os.getenv("YOSAI_ENV", "development").lower()
        self.environment = env

        base = Path("config")
        if env == "production":
            return base / "production.yaml"
        elif env == "test":
            return base / "test.yaml"
        else:
            return base / "config.yaml"

    def _substitute_env_vars(self, content: str) -> str:
        def repl(match: re.Match[str]) -> str:
            expr = match.group(1)
            if ":" in expr:
                name, default = expr.split(":", 1)
                return os.getenv(name, default)
            return os.getenv(expr, "")

        return self._env_pattern.sub(repl, content)

    def _apply_dict(self, data: Dict[str, Any]) -> None:
        self._update_dataclass(self.app_config, data.get("app", {}))
        self._update_dataclass(self.database_config, data.get("database", {}))
        self._update_dataclass(self.cache_config, data.get("cache", {}))
        self._update_dataclass(self.security_config, data.get("security", {}))
        self._update_dataclass(self.analytics_config, data.get("analytics", {}))
        self._update_dataclass(self.monitoring_config, data.get("monitoring", {}))
        self._update_dataclass(self.logging_config, data.get("logging", {}))

    def _update_dataclass(self, instance: Any, values: Dict[str, Any]) -> None:
        for f in fields(instance):
            if f.name in values:
                setattr(instance, f.name, values[f.name])

    def _apply_env_overrides(self) -> None:
        mapping = {
            ("app", "debug"): "DEBUG",
            ("app", "host"): "HOST",
            ("app", "port"): "PORT",
            ("app", "title"): "YOSAI_APP_TITLE",
            ("database", "type"): "DB_TYPE",
            ("database", "host"): "DB_HOST",
            ("database", "port"): "DB_PORT",
            ("database", "name"): "DB_NAME",
            ("database", "user"): "DB_USER",
            ("database", "password"): "DB_PASSWORD",
            ("cache", "type"): "CACHE_TYPE",
            ("cache", "host"): "CACHE_HOST",
            ("cache", "port"): "CACHE_PORT",
            ("cache", "ttl"): "CACHE_TTL",
            ("security", "secret_key"): "SECRET_KEY",
            ("security", "session_timeout"): "SESSION_TIMEOUT",
        }

        for (section, key), env_var in mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                inst = getattr(self, f"{section}_config")
                field_type = type(getattr(inst, key))
                converted = self._convert(value, field_type)
                setattr(inst, key, converted)

    def _convert(self, value: str, target_type: type) -> Any:
        if target_type is bool:
            return value.lower() in {"1", "true", "yes", "on"}
        if target_type is int:
            try:
                return int(value)
            except ValueError:
                return 0
        return target_type(value)


# ---------------------------------------------------------------------------
# Singleton helper
# ---------------------------------------------------------------------------

_configuration_manager: Optional[ConfigurationManager] = None


def get_configuration_manager() -> ConfigurationManager:
    """Return a singleton ``ConfigurationManager`` instance."""
    global _configuration_manager
    if _configuration_manager is None:
        _configuration_manager = ConfigurationManager()
        _configuration_manager.load_configuration(None)
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
]
