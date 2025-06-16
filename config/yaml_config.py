import os
import yaml
from dataclasses import dataclass, fields
from typing import Optional, Any, Dict

@dataclass
class AppConfig:
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8050
    title: str = "Y\u014dsai Intel Dashboard"
    timezone: str = "UTC"
    log_level: str = "INFO"
    enable_profiling: bool = False

@dataclass
class DatabaseConfig:
    type: str = "mock"
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 5
    ssl_mode: Optional[str] = None
    connection_timeout: Optional[int] = None

@dataclass
class CacheConfig:
    type: str = "memory"
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[int] = None
    timeout_seconds: int = 300
    max_memory_mb: Optional[int] = None
    key_prefix: str = ""

@dataclass
class SecurityConfig:
    secret_key: str = "dev-key-change-in-production"
    session_timeout_minutes: int = 60
    max_file_size_mb: int = 100
    allowed_file_types: Optional[list] = None
    cors_enabled: bool = False
    cors_origins: Optional[list] = None

@dataclass
class AnalyticsConfig:
    cache_timeout_seconds: int = 300
    max_records_per_query: int = 10000
    enable_real_time: bool = True
    batch_size: int = 1000
    anomaly_detection_enabled: bool = True
    ml_models_path: str = "models/ml"

@dataclass
class MonitoringConfig:
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    health_check_interval_seconds: int = 30
    performance_monitoring: bool = False
    error_reporting_enabled: bool = False
    sentry_dsn: Optional[str] = None

class ConfigurationManager:
    """Load configuration from YAML and expose typed access."""

    def __init__(self) -> None:
        self.app_config = AppConfig()
        self.database_config = DatabaseConfig()
        self.cache_config = CacheConfig()
        self.security_config = SecurityConfig()
        self.analytics_config = AnalyticsConfig()
        self.monitoring_config = MonitoringConfig()

    @staticmethod
    def _update_dataclass(obj: Any, data: Dict[str, Any]) -> None:
        for field in fields(obj):
            if field.name in data:
                setattr(obj, field.name, data[field.name])

    def load_configuration(self, path: Optional[str] = None) -> None:
        """Load configuration from the given YAML file."""
        config_path = path or os.path.join("config", "config.yaml")
        if not os.path.exists(config_path):
            return
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}
        self._update_dataclass(self.app_config, config_data.get("app", {}))
        self._update_dataclass(self.database_config, config_data.get("database", {}))
        self._update_dataclass(self.cache_config, config_data.get("cache", {}))
        self._update_dataclass(self.security_config, config_data.get("security", {}))
        self._update_dataclass(self.analytics_config, config_data.get("analytics", {}))
        self._update_dataclass(self.monitoring_config, config_data.get("monitoring", {}))

    def print_startup_info(self) -> None:
        print("\n" + "=" * 60)
        print("\U0001f3ef Y\u014dsai Intel Dashboard")
        print("=" * 60)
        print(f"\U0001f310 URL: http://{self.app_config.host}:{self.app_config.port}")
        print(f"\U0001f527 Debug Mode: {self.app_config.debug}")
        print(f"\U0001f4ca Analytics: http://{self.app_config.host}:{self.app_config.port}/analytics")
        print("=" * 60)
        if self.app_config.debug:
            print("\u26a0\ufe0f  Running in DEBUG mode - do not use in production!")
        print("\n\U0001f680 Dashboard starting...")
