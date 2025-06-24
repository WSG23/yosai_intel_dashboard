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
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    raw = f.read()
                substituted = self._substitute_env_vars(raw)
                data = yaml.safe_load(substituted) or {}
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")

        self._apply_dict(data)
        self._apply_env_overrides()
        self._ensure_production_env_vars()

    def get_app_config(self) -> AppConfig:
        return self.app_config

    def get_database_config(self) -> DatabaseConfig:
        return self.database_config

    def get_cache_config(self) -> CacheConfig:
        return self.cache_config

    def get_security_config(self) -> SecurityConfig:
        return self.security_config

    def get_analytics_config(self) -> AnalyticsConfig:
        return self.analytics_config

    def get_monitoring_config(self) -> MonitoringConfig:
        return self.monitoring_config

    def get_logging_config(self) -> LoggingConfig:
        return self.logging_config

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
    def _determine_config_file(self, path: Optional[str]) -> Optional[Path]:
        if path:
            return Path(path)

        env_file = os.getenv("YOSAI_CONFIG_FILE")
        if env_file:
            return Path(env_file)

        env = os.getenv("YOSAI_ENV", "development").lower()
        self.environment = env

        base = Path("config")
        if env == "production":
            candidate = base / "production.yaml"
        elif env == "test":
            candidate = base / "test.yaml"
        else:
            candidate = base / "config.yaml"
        
        # Return None if file doesn't exist (we'll use defaults)
        return candidate if candidate.exists() else None

    def _substitute_env_vars(self, content: str) -> str:
        """Replace ${VAR_NAME} with environment variable values."""
        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return self._env_pattern.sub(replacer, content)

    def _apply_dict(self, data: Dict[str, Any]) -> None:
        """Apply configuration from dictionary."""
        if "app" in data:
            self._update_dataclass(self.app_config, data["app"])
        if "database" in data:
            self._update_dataclass(self.database_config, data["database"])
        if "cache" in data:
            self._update_dataclass(self.cache_config, data["cache"])
        if "security" in data:
            self._update_dataclass(self.security_config, data["security"])
        if "analytics" in data:
            self._update_dataclass(self.analytics_config, data["analytics"])
        if "monitoring" in data:
            self._update_dataclass(self.monitoring_config, data["monitoring"])
        if "logging" in data:
            self._update_dataclass(self.logging_config, data["logging"])

    def _update_dataclass(self, obj: Any, data: Dict[str, Any]) -> None:
        """Update dataclass object with data from dict."""
        for field_info in fields(obj):
            if field_info.name in data:
                setattr(obj, field_info.name, data[field_info.name])

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # App config
        if os.getenv("DEBUG"):
            self.app_config.debug = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        if os.getenv("HOST"):
            self.app_config.host = os.getenv("HOST", self.app_config.host)
        if os.getenv("PORT"):
            self.app_config.port = int(os.getenv("PORT", self.app_config.port))

        # Database config
        if os.getenv("DB_TYPE"):
            self.database_config.type = os.getenv("DB_TYPE", self.database_config.type)
        if os.getenv("DB_HOST"):
            self.database_config.host = os.getenv("DB_HOST", self.database_config.host)
        if os.getenv("DB_PORT"):
            self.database_config.port = int(os.getenv("DB_PORT", self.database_config.port))
        if os.getenv("DB_NAME"):
            self.database_config.name = os.getenv("DB_NAME", self.database_config.name)
        if os.getenv("DB_USER"):
            self.database_config.user = os.getenv("DB_USER", self.database_config.user)
        if os.getenv("DB_PASSWORD"):
            self.database_config.password = os.getenv("DB_PASSWORD", self.database_config.password)

        # Security config
        if os.getenv("SECRET_KEY"):
            self.security_config.secret_key = os.getenv("SECRET_KEY", self.security_config.secret_key)

    def _ensure_production_env_vars(self) -> None:
        """Ensure required environment variables for production."""
        if self.environment == "production":
            required_vars = ["SECRET_KEY", "DB_PASSWORD"]
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                raise ValueError(f"Production environment requires these environment variables: {missing}")


# ---------------------------------------------------------------------------
# Global instance
# ---------------------------------------------------------------------------

_config_manager: Optional[ConfigurationManager] = None


def get_configuration_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager.from_environment()
    return _config_manager


# Legacy compatibility functions
def get_app_config() -> AppConfig:
    return get_configuration_manager().get_app_config()


def get_database_config() -> DatabaseConfig:
    return get_configuration_manager().get_database_config()


def get_cache_config() -> CacheConfig:
    return get_configuration_manager().get_cache_config()


def get_security_config() -> SecurityConfig:
    return get_configuration_manager().get_security_config()


def get_analytics_config() -> AnalyticsConfig:
    return get_configuration_manager().get_analytics_config()


def get_monitoring_config() -> MonitoringConfig:
    return get_configuration_manager().get_monitoring_config()


def get_logging_config() -> LoggingConfig:
    return get_configuration_manager().get_logging_config()
