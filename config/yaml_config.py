# config/yaml_config.py - FIXED: Added from_environment class method
"""
YAML Configuration System with Environment Support
Enhanced modular configuration with proper class method support
"""
import os
from core.secret_manager import SecretManager
import re
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field, fields
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration"""

    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8050
    title: str = "Yōsai Intel Dashboard"
    log_level: str = "INFO"
    app_name: str = "Yōsai Intel Dashboard"
    enable_profiling: bool = False
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(
        default_factory=lambda: [".csv", ".json", ".xlsx", ".xls"]
    )
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)


@dataclass
class DatabaseConfig:
    """Database configuration"""

    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "yosai_dashboard.db"
    username: str = "yosai_user"
    password: str = ""
    pool_size: int = 5
    echo: bool = False


@dataclass
class CacheConfig:
    """Cache configuration"""

    type: str = "memory"
    host: str = "localhost"
    port: int = 6379
    timeout_seconds: int = 300
    max_size: int = 1000


@dataclass
class SecurityConfig:
    """Security configuration"""

    secret_key: Optional[str] = None
    session_timeout_minutes: int = 30
    max_login_attempts: int = 5
    enable_csrf: bool = True
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(
        default_factory=lambda: [".csv", ".json", ".xlsx", ".xls"]
    )
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)


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


class EnvironmentOverrideProcessor:
    """Processes environment variable overrides for configuration"""

    @staticmethod
    def process_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """Process environment variable overrides"""

        # Define mapping of environment variables to config paths
        env_mappings = {
            # Database
            "DB_HOST": "database.host",
            "DB_PORT": "database.port",
            "DB_NAME": "database.database",
            "DB_USER": "database.username",
            "DB_PASSWORD": "database.password",
            "DB_TYPE": "database.type",
            "DB_POOL_SIZE": "database.pool_size",
            # App
            "DEBUG": "app.debug",
            "HOST": "app.host",
            "PORT": "app.port",
            "LOG_LEVEL": "app.log_level",
            # Cache
            "REDIS_HOST": "cache.host",
            "REDIS_PORT": "cache.port",
            "CACHE_TIMEOUT": "cache.timeout_seconds",
            # Security
            "SECRET_KEY": "security.secret_key",
            "MAX_FILE_SIZE_MB": "security.max_file_size_mb",
            # Monitoring
            "SENTRY_DSN": "monitoring.sentry_dsn",
            "ENABLE_MONITORING": "monitoring.metrics_enabled",
        }

        # Process each environment variable
        manager = SecretManager()
        for env_var, config_path in env_mappings.items():
            try:
                env_value = manager.get(env_var)
            except KeyError:
                env_value = None
            if env_value is not None:
                EnvironmentOverrideProcessor._set_nested_value(
                    config,
                    config_path,
                    EnvironmentOverrideProcessor._convert_value(env_value),
                )

        # Process generic overrides (YOSAI_<SECTION>_<KEY> format)
        EnvironmentOverrideProcessor._process_generic_overrides(config)

        return config

    @staticmethod
    def _set_nested_value(config: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested value in config dictionary"""
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    @staticmethod
    def _convert_value(value: str) -> Any:
        """Convert string value to appropriate type"""
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        if value.isdigit():
            return int(value)

        try:
            return float(value)
        except ValueError:
            return value

    @staticmethod
    def _process_generic_overrides(config: Dict[str, Any]) -> None:
        """Process YOSAI_<SECTION>_<KEY> environment variables"""
        for env_var, env_value in os.environ.items():
            if env_var.startswith("YOSAI_"):
                # Remove YOSAI_ prefix and convert to config path
                config_path = env_var[6:].lower().replace("_", ".")

                # Log the override for debugging
                logger.debug(f"Environment override: {env_var} -> {config_path}")

                EnvironmentOverrideProcessor._set_nested_value(
                    config,
                    config_path,
                    EnvironmentOverrideProcessor._convert_value(env_value),
                )


class ConfigurationValidator:
    """Validates configuration for common issues"""

    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of warnings/errors"""
        warnings = []

        # App validation
        app_config = config.get("app", {})
        if app_config.get("debug", False) and app_config.get("host") == "0.0.0.0":
            warnings.append(
                "WARNING: Debug mode enabled with host 0.0.0.0 - security risk"
            )

        # Security validation
        security_config = config.get("security", {})
        if not security_config.get("secret_key"):
            warnings.append("WARNING: SECRET_KEY not configured")

        # Database validation
        db_config = config.get("database", {})
        if db_config.get("type") == "postgresql" and not db_config.get("password"):
            warnings.append("WARNING: PostgreSQL configured without password")

        # Monitoring validation
        monitoring_config = config.get("monitoring", {})
        if monitoring_config.get(
            "error_reporting_enabled", False
        ) and not monitoring_config.get("sentry_dsn"):
            warnings.append(
                "WARNING: Error reporting enabled but no Sentry DSN configured"
            )

        return warnings


class ConfigurationError(Exception):
    """Configuration-related errors"""

    pass


class ConfigurationManager:
    """Main configuration manager with YAML support and environment overrides"""

    def __init__(
        self, config_path: Optional[str] = None, environment: Optional[str] = None
    ):
        """Initialize configuration manager"""
        self._raw_config: Dict[str, Any] = {}
        self.app_config: AppConfig = AppConfig()
        self.database_config: DatabaseConfig = DatabaseConfig()
        self.cache_config: CacheConfig = CacheConfig()
        self.security_config: SecurityConfig = SecurityConfig()
        self.analytics_config: AnalyticsConfig = AnalyticsConfig()
        self.monitoring_config: MonitoringConfig = MonitoringConfig()
        self._loaded_files: List[str] = []
        self._warnings: List[str] = []
        self._config_path = config_path
        manager = SecretManager()
        self._environment = environment or manager.get("ENVIRONMENT", "development")

    @classmethod
    def from_environment(
        cls, environment: Optional[str] = None
    ) -> "ConfigurationManager":
        """Create ConfigurationManager instance configured for specific environment"""
        manager = SecretManager()
        env = environment or manager.get("ENVIRONMENT", "development")

        # Determine config file path based on environment
        config_dir = Path("config")
        config_path = None

        # Try environment-specific file first
        env_config_file = config_dir / f"{env}.yaml"
        if env_config_file.exists():
            config_path = str(env_config_file)
        else:
            # Try generic config.yaml
            generic_config_file = config_dir / "config.yaml"
            if generic_config_file.exists():
                config_path = str(generic_config_file)
            else:
                # Create basic config if none exists
                logger.warning(
                    f"No configuration file found for environment '{env}', using defaults"
                )

        # Create instance and load configuration
        instance = cls(config_path=config_path, environment=env)
        instance.load_configuration()
        return instance

    def load_configuration(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML files with environment overrides"""
        try:
            # Load base configuration
            effective_path = config_path or self._config_path
            if effective_path and Path(effective_path).exists():

                self._load_yaml_file(effective_path)
                logger.info(f"Loaded configuration from: {effective_path}")
            else:
                logger.info("No configuration file specified, using defaults")
                self._raw_config = self._get_default_config()

            # Apply environment variable overrides
            self._raw_config = EnvironmentOverrideProcessor.process_overrides(
                self._raw_config
            )

            # Load into dataclass configurations
            self._load_section("app", self.app_config, self._raw_config)
            self._load_section("database", self.database_config, self._raw_config)
            self._load_section("cache", self.cache_config, self._raw_config)
            self._load_section("security", self.security_config, self._raw_config)
            self._load_section("analytics", self.analytics_config, self._raw_config)
            self._load_section("monitoring", self.monitoring_config, self._raw_config)

            # Validate configuration
            self._warnings = ConfigurationValidator.validate(self._raw_config)

            logger.info(
                f"Configuration loaded successfully for environment: {self._environment}"
            )

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")

    def _load_yaml_file(self, file_path: str) -> None:
        """Load and parse YAML configuration file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Process environment variable substitutions
            content = self._substitute_environment_variables(content)

            # Parse YAML
            config_data = yaml.safe_load(content) or {}

            # Merge with existing config (for multiple file support)
            self._raw_config = {**self._raw_config, **config_data}
            self._loaded_files.append(file_path)

        except Exception as e:
            logger.error(f"Error loading YAML file {file_path}: {e}")
            raise ConfigurationError(f"Failed to load YAML file: {e}")

    def _substitute_environment_variables(self, content: str) -> str:
        """Substitute ${VAR} and ${VAR:default} patterns with environment variables"""

        def replace_env_var(match):
            var_expr = match.group(1)

            # Handle ${VAR:default} syntax
            if ":" in var_expr:
                var_name, default_value = var_expr.split(":", 1)
                manager = SecretManager()
                return manager.get(var_name.strip(), default_value.strip())
            else:
                # Handle ${VAR} syntax
                var_name = var_expr.strip()
                manager = SecretManager()
                value = manager.get(var_name, None)
                if value is None:
                    raise ConfigurationError(
                        f"Environment variable '{var_name}' not set and no default provided"
                    )
                return value

        # Pattern to match ${VAR} or ${VAR:default}
        pattern = r"\$\{([^}]+)\}"
        return re.sub(pattern, replace_env_var, content)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when no file is available"""
        return {
            "app": {
                "debug": self._environment == "development",
                "host": "127.0.0.1",
                "port": 8050,
                "title": "Yōsai Intel Dashboard",
                "log_level": "DEBUG" if self._environment == "development" else "INFO",
                "app_name": "Yōsai Intel Dashboard",
            },
            "database": {"type": "sqlite", "database": f"yosai_{self._environment}.db"},
            "cache": {"type": "memory"},
            "security": {"secret_key": None},
            "analytics": {},
            "monitoring": {
                "health_check_enabled": True,
                "metrics_enabled": self._environment == "production",
            },
        }

    def _load_section(
        self, section_name: str, config_obj: Any, config_data: Dict[str, Any]
    ) -> None:
        """Load configuration section with error handling"""
        try:
            section_data = config_data.get(section_name, {})
            self._update_dataclass(config_obj, section_data)
            logger.debug(f"Loaded {section_name} configuration")
        except Exception as e:
            logger.error(f"Error loading {section_name} configuration: {e}")
            raise ConfigurationError(f"Invalid {section_name} configuration: {e}")

    @staticmethod
    def _update_dataclass(obj: Any, data: Dict[str, Any]) -> None:
        """Update dataclass with validation"""
        for field_info in fields(obj):
            if field_info.name in data:
                try:
                    setattr(obj, field_info.name, data[field_info.name])
                except Exception as e:
                    logger.warning(f"Failed to set {field_info.name}: {e}")

    def get_effective_configuration(self) -> Dict[str, Any]:
        """Get the effective configuration as dictionary"""
        return self._raw_config.copy()

    def get_loaded_files(self) -> List[str]:
        """Get list of loaded configuration files"""
        return self._loaded_files.copy()

    def validate_configuration(self) -> List[str]:
        """Validate configuration and return warnings"""
        return self._warnings.copy()

    def save_effective_config(self, output_path: str) -> None:
        """Save the effective configuration to a file for debugging"""
        effective_config = self.get_effective_configuration()

        # Remove sensitive information
        if "password" in effective_config.get("database", {}):
            effective_config["database"]["password"] = "[REDACTED]"
        if "secret_key" in effective_config.get("security", {}):
            effective_config["security"]["secret_key"] = "[REDACTED]"

        with open(output_path, "w") as f:
            yaml.dump(effective_config, f, default_flow_style=False, indent=2)

        logger.info(f"Effective configuration saved to: {output_path}")

    def print_startup_info(self) -> None:
        """Print startup information similar to the legacy ConfigManager"""
        print("\n" + "=" * 60)
        print("🏯 YŌSAI INTEL DASHBOARD")
        print("=" * 60)
        print(f"🌐 URL: http://{self.app_config.host}:{self.app_config.port}")
        print(f"🔧 Debug Mode: {self.app_config.debug}")
        print(
            f"📊 Analytics: http://{self.app_config.host}:{self.app_config.port}/analytics"
        )
        print("=" * 60)
        if self.app_config.debug:
            print("⚠️  Running in DEBUG mode - do not use in production!")
        print("\n🚀 Dashboard starting...")


# Factory function for dependency injection
def create_configuration_manager() -> ConfigurationManager:
    """Factory function to create and load configuration manager"""
    manager = ConfigurationManager()
    manager.load_configuration()
    return manager


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_configuration_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = create_configuration_manager()
    return _config_manager


def reset_configuration_manager() -> None:
    """Reset global configuration manager (useful for testing)"""
    global _config_manager
    _config_manager = None


# Export key classes and functions
__all__ = [
    "ConfigurationManager",
    "AppConfig",
    "DatabaseConfig",
    "CacheConfig",
    "SecurityConfig",
    "AnalyticsConfig",
    "MonitoringConfig",
    "ConfigurationError",
    "create_configuration_manager",
    "get_configuration_manager",
    "reset_configuration_manager",
]
