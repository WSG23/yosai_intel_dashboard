# config/unified_config.py
"""
Unified configuration system that consolidates YAML and environment-based configs
Inspired by Apple's configuration management patterns
"""
import os
import yaml
from typing import Dict, Any, Optional, Type, TypeVar, Generic
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

T = TypeVar('T')

class Environment(Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigurationError(Exception):
    """Configuration-related errors"""
    pass

@dataclass
class DatabaseConfig:
    """Database configuration section"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "yosai_intel"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 5
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    
    @property
    def connection_string(self) -> str:
        """Build connection string based on database type"""
        if self.type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.type == "sqlite":
            return f"sqlite:///{self.name}.db"
        elif self.type == "mock":
            return "mock://memory"
        else:
            raise ConfigurationError(f"Unsupported database type: {self.type}")

@dataclass
class SecurityConfig:
    """Security configuration section"""
    secret_key: str = "change-this-in-production"
    session_timeout: int = 3600
    max_login_attempts: int = 5
    rate_limit_per_minute: int = 100
    allowed_file_extensions: list = field(default_factory=lambda: ['.csv', '.xlsx', '.json'])
    max_file_size_mb: int = 100
    cors_origins: list = field(default_factory=list)

@dataclass
class AppConfig:
    """Application configuration section"""
    name: str = "Yōsai Intel Dashboard"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8050
    log_level: str = "INFO"
    timezone: str = "UTC"
    language: str = "en"

@dataclass
class AnalyticsConfig:
    """Analytics configuration section"""
    cache_timeout: int = 300
    max_records_per_query: int = 10000
    anomaly_detection_threshold: float = 0.8
    batch_processing_size: int = 1000
    enable_real_time_processing: bool = True
    data_retention_days: int = 365

@dataclass
class UIConfig:
    """User interface configuration section"""
    theme: str = "dark"
    refresh_interval: int = 30
    max_chart_points: int = 1000
    enable_animations: bool = True
    default_page_size: int = 25
    available_themes: list = field(default_factory=lambda: ["dark", "light", "high-contrast"])

@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    error_reporting_enabled: bool = True
    performance_logging: bool = False
    sentry_dsn: Optional[str] = None

@dataclass
class YosaiConfiguration:
    """Complete application configuration"""
    environment: Environment = Environment.DEVELOPMENT
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    app: AppConfig = field(default_factory=AppConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    def validate(self) -> None:
        """Validate configuration values"""
        errors = []
        
        # Database validation
        if self.database.type not in ["postgresql", "sqlite", "mock"]:
            errors.append(f"Invalid database type: {self.database.type}")
        
        if self.database.port < 1 or self.database.port > 65535:
            errors.append(f"Invalid database port: {self.database.port}")
        
        # Security validation
        if self.environment == Environment.PRODUCTION:
            if self.security.secret_key == "change-this-in-production":
                errors.append("Secret key must be changed for production")
            
            if self.app.debug:
                errors.append("Debug mode must be disabled in production")
        
        # App validation
        if self.app.port < 1 or self.app.port > 65535:
            errors.append(f"Invalid app port: {self.app.port}")
        
        if self.app.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append(f"Invalid log level: {self.app.log_level}")
        
        # Analytics validation
        if self.analytics.anomaly_detection_threshold < 0 or self.analytics.anomaly_detection_threshold > 1:
            errors.append("Anomaly detection threshold must be between 0 and 1")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")

class ConfigurationManager:
    """
    Unified configuration manager that handles YAML files and environment overrides
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config: Optional[YosaiConfiguration] = None
        self._config_file_path: Optional[str] = None
    
    def load_configuration(self, config_file: Optional[str] = None) -> YosaiConfiguration:
        """Load configuration from file and environment"""
        
        # Determine configuration file
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = self._get_default_config_path()
        
        self._config_file_path = str(config_path)
        
        # Load base configuration from YAML
        if config_path.exists():
            self.config = self._load_from_yaml(config_path)
            self.logger.info(f"Loaded configuration from: {config_path}")
        else:
            self.config = YosaiConfiguration()
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
        
        # Apply environment overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self.config.validate()
        
        self.logger.info(f"Configuration loaded for environment: {self.config.environment.value}")
        return self.config
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path based on environment"""
        env = os.getenv('YOSAI_ENV', 'development').lower()
        
        config_dir = Path('config')
        config_files = {
            'development': config_dir / 'development.yaml',
            'staging': config_dir / 'staging.yaml',
            'production': config_dir / 'production.yaml',
            'testing': config_dir / 'testing.yaml'
        }
        
        return config_files.get(env, config_dir / 'config.yaml')
    
    def _load_from_yaml(self, config_path: Path) -> YosaiConfiguration:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            # Convert flat YAML structure to nested dataclass structure
            return self._dict_to_config(data)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> YosaiConfiguration:
        """Convert dictionary to configuration dataclass"""
        
        # Extract sections from flat or nested structure
        config_dict = {
            'environment': Environment(data.get('environment', 'development')),
            'database': self._extract_section(data, 'database', DatabaseConfig),
            'security': self._extract_section(data, 'security', SecurityConfig),
            'app': self._extract_section(data, 'app', AppConfig),
            'analytics': self._extract_section(data, 'analytics', AnalyticsConfig),
            'ui': self._extract_section(data, 'ui', UIConfig),
            'monitoring': self._extract_section(data, 'monitoring', MonitoringConfig)
        }
        
        return YosaiConfiguration(**config_dict)
    
    def _extract_section(self, data: Dict[str, Any], section_name: str, config_class: Type[T]) -> T:
        """Extract and create configuration section"""
        section_data = data.get(section_name, {})
        
        # Filter only valid fields for the dataclass
        field_names = {f.name for f in config_class.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in section_data.items() if k in field_names}
        
        return config_class(**filtered_data)
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides"""
        if not self.config:
            return
        
        # Environment mapping
        env_mappings = {
            # Database
            'DB_TYPE': ('database', 'type'),
            'DB_HOST': ('database', 'host'),
            'DB_PORT': ('database', 'port'),
            'DB_NAME': ('database', 'name'),
            'DB_USER': ('database', 'username'),
            'DB_PASSWORD': ('database', 'password'),
            'DB_POOL_SIZE': ('database', 'pool_size'),
            
            # Security
            'SECRET_KEY': ('security', 'secret_key'),
            'MAX_FILE_SIZE_MB': ('security', 'max_file_size_mb'),
            
            # App
            'DEBUG': ('app', 'debug'),
            'HOST': ('app', 'host'),
            'PORT': ('app', 'port'),
            'LOG_LEVEL': ('app', 'log_level'),
            
            # Analytics
            'CACHE_TIMEOUT': ('analytics', 'cache_timeout'),
            'MAX_RECORDS_PER_QUERY': ('analytics', 'max_records_per_query'),
            
            # Monitoring
            'SENTRY_DSN': ('monitoring', 'sentry_dsn'),
        }
        
        for env_var, (section, field) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_config_value(section, field, value)
    
    def _set_config_value(self, section: str, field: str, value: str) -> None:
        """Set configuration value with proper type conversion"""
        if not self.config:
            return
        
        section_obj = getattr(self.config, section)
        field_type = type(getattr(section_obj, field))
        
        # Convert string value to appropriate type
        try:
            if field_type == bool:
                converted_value = value.lower() in ('true', '1', 'yes', 'on')
            elif field_type == int:
                converted_value = int(value)
            elif field_type == float:
                converted_value = float(value)
            else:
                converted_value = value
            
            setattr(section_obj, field, converted_value)
            self.logger.debug(f"Override applied: {section}.{field} = {converted_value}")
            
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Failed to convert {section}.{field} = {value}: {e}")
    
    def get_config(self) -> YosaiConfiguration:
        """Get current configuration"""
        if not self.config:
            return self.load_configuration()
        return self.config
    
    def reload_configuration(self) -> YosaiConfiguration:
        """Reload configuration from file"""
        return self.load_configuration(self._config_file_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        if not self.config:
            return {}
        
        # Use dataclass asdict equivalent
        from dataclasses import asdict
        return asdict(self.config)
    
    def print_configuration_summary(self) -> None:
        """Print configuration summary for debugging"""
        if not self.config:
            print("No configuration loaded")
            return
        
        print("🔧 Yōsai Configuration Summary")
        print("=" * 40)
        print(f"Environment: {self.config.environment.value}")
        print(f"Database: {self.config.database.type} @ {self.config.database.host}:{self.config.database.port}")
        print(f"Application: {self.config.app.host}:{self.config.app.port} (debug={self.config.app.debug})")
        print(f"Log Level: {self.config.app.log_level}")
        print("=" * 40)

    def print_startup_info(self) -> None:
        """Print startup information similar to yaml_config"""
        if not self.config:
            print("Configuration not loaded")
            return

        print("\n" + "=" * 60)
        print("🏯 YŌSAI INTEL DASHBOARD")
        print("=" * 60)
        print(f"🌐 URL: http://{self.config.app.host}:{self.config.app.port}")
        print(f"🔧 Debug Mode: {self.config.app.debug}")
        print(f"📊 Analytics: http://{self.config.app.host}:{self.config.app.port}/analytics")
        print("=" * 60)
        if self.config.app.debug:
            print("⚠️  Running in DEBUG mode - do not use in production!")
        print("\n🚀 Dashboard starting...")

# Global configuration manager
config_manager = ConfigurationManager()

def get_config() -> YosaiConfiguration:
    """Get global configuration"""
    return config_manager.get_config()

def reload_config() -> YosaiConfiguration:
    """Reload global configuration"""
    return config_manager.reload_configuration()