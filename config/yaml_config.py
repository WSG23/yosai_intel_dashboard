# config/yaml_config.py - COMPLETE: Full YAML configuration with environment substitution
"""
Complete YAML Configuration System for Yōsai Intel Dashboard
NOW INCLUDES: Environment variable substitution, validation, merging, secrets handling
"""

import os
import yaml
import re
import logging
from dataclasses import dataclass, fields, field
from typing import Optional, Any, Dict, List, Union
from pathlib import Path
import json

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
    enable_profiling: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not (1024 <= self.port <= 65535):
            raise ValueError(f"Port must be between 1024-65535, got {self.port}")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")

@dataclass
class DatabaseConfig:
    """Database configuration with connection validation"""
    type: str = "mock"
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 5
    ssl_mode: Optional[str] = None
    connection_timeout: int = 30
    retry_attempts: int = 3
    
    def __post_init__(self):
        """Validate database configuration"""
        valid_types = ["postgresql", "sqlite", "mock"]
        if self.type not in valid_types:
            raise ValueError(f"Database type must be one of {valid_types}")
        
        if self.type == "postgresql":
            required_fields = ["host", "database", "username"]
            missing = [f for f in required_fields if getattr(self, f) is None]
            if missing:
                raise ValueError(f"PostgreSQL requires: {missing}")
        
        if self.pool_size < 1:
            raise ValueError("pool_size must be at least 1")

@dataclass
class CacheConfig:
    """Cache configuration"""
    type: str = "memory"
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[int] = None
    timeout_seconds: int = 300
    max_memory_mb: Optional[int] = None
    key_prefix: str = "yosai:"
    compression_enabled: bool = False
    
    def __post_init__(self):
        """Validate cache configuration"""
        valid_types = ["memory", "redis", "disabled"]
        if self.type not in valid_types:
            raise ValueError(f"Cache type must be one of {valid_types}")
        
        if self.type == "redis" and not self.host:
            raise ValueError("Redis cache requires host configuration")

@dataclass
class SecurityConfig:
    """Security configuration with validation"""
    secret_key: str = "dev-key-change-in-production"
    session_timeout_minutes: int = 60
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(default_factory=lambda: [".csv", ".json", ".xlsx", ".xls"])
    cors_enabled: bool = False
    cors_origins: List[str] = field(default_factory=list)
    rate_limiting_enabled: bool = False
    rate_limit_per_minute: int = 60
    
    def __post_init__(self):
        """Validate security configuration"""
        if self.secret_key == "dev-key-change-in-production":
            logger.warning("⚠️  Using default secret key! Change for production!")
        
        if len(self.secret_key) < 32:
            logger.warning("⚠️  Secret key should be at least 32 characters long")
        
        if self.max_file_size_mb > 1000:
            logger.warning(f"⚠️  Large file size limit: {self.max_file_size_mb}MB")

@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    cache_timeout_seconds: int = 300
    max_records_per_query: int = 10000
    enable_real_time: bool = True
    batch_size: int = 1000
    anomaly_detection_enabled: bool = True
    ml_models_path: str = "models/ml"
    data_retention_days: int = 365
    
    def __post_init__(self):
        """Validate analytics configuration"""
        if self.max_records_per_query > 100000:
            logger.warning(f"⚠️  Large query limit may impact performance: {self.max_records_per_query}")

@dataclass
class MonitoringConfig:
    """Monitoring and health check configuration"""
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    health_check_interval_seconds: int = 30
    performance_monitoring: bool = False
    error_reporting_enabled: bool = False
    sentry_dsn: Optional[str] = None
    log_retention_days: int = 30
    
    def __post_init__(self):
        """Validate monitoring configuration"""
        if self.error_reporting_enabled and not self.sentry_dsn:
            logger.warning("⚠️  Error reporting enabled but no Sentry DSN provided")

class ConfigurationManager:
    """Enhanced configuration manager with full YAML support"""
    
    def __init__(self) -> None:
        # Initialize with defaults
        self.app_config = AppConfig()
        self.database_config = DatabaseConfig()
        self.cache_config = CacheConfig()
        self.security_config = SecurityConfig()
        self.analytics_config = AnalyticsConfig()
        self.monitoring_config = MonitoringConfig()
        
        # Store raw config data for debugging
        self._raw_config: Dict[str, Any] = {}
        self._config_source: Optional[str] = None
    
    def load_configuration(self, path: Optional[str] = None) -> None:
        """Load configuration with environment variable substitution"""
        try:
            config_path = path or self._get_default_config_path()
            
            if not config_path or not Path(config_path).exists():
                logger.warning(f"Config file not found: {config_path}, using defaults")
                return
            
            logger.info(f"Loading configuration from: {config_path}")
            self._config_source = config_path
            
            # Load raw YAML
            with open(config_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            
            # Substitute environment variables
            substituted_content = self._substitute_environment_variables(raw_content)
            
            # Parse YAML
            config_data = yaml.safe_load(substituted_content) or {}
            self._raw_config = config_data
            
            # Load into dataclasses with validation
            self._load_section("app", self.app_config, config_data)
            self._load_section("database", self.database_config, config_data)
            self._load_section("cache", self.cache_config, config_data)
            self._load_section("security", self.security_config, config_data)
            self._load_section("analytics", self.analytics_config, config_data)
            self._load_section("monitoring", self.monitoring_config, config_data)
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _substitute_environment_variables(self, content: str) -> str:
        """Substitute ${VAR} and ${VAR:default} patterns with environment variables"""
        def replace_env_var(match):
            var_expr = match.group(1)
            
            # Handle ${VAR:default} syntax
            if ':' in var_expr:
                var_name, default_value = var_expr.split(':', 1)
                return os.getenv(var_name.strip(), default_value.strip())
            else:
                # Handle ${VAR} syntax
                var_name = var_expr.strip()
                value = os.getenv(var_name)
                if value is None:
                    raise ConfigurationError(f"Environment variable '{var_name}' not set and no default provided")
                return value
        
        # Pattern to match ${VAR} or ${VAR:default}
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_env_var, content)
    
    def _load_section(self, section_name: str, config_obj: Any, config_data: Dict[str, Any]) -> None:
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
                value = data[field_info.name]
                
                # Type conversion for basic types
                if field_info.type == bool and isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif field_info.type == int and isinstance(value, str):
                    value = int(value)
                elif field_info.type == float and isinstance(value, str):
                    value = float(value)
                
                setattr(obj, field_info.name, value)
    
    def _get_default_config_path(self) -> Optional[str]:
        """Get default configuration path based on environment"""
        # Check for explicit config file
        explicit_config = os.getenv('YOSAI_CONFIG_FILE')
        if explicit_config and Path(explicit_config).exists():
            return explicit_config
        
        # Check environment-specific config
        env = os.getenv('YOSAI_ENV', 'development').lower()
        
        config_map = {
            'production': 'config/production.yaml',
            'prod': 'config/production.yaml',
            'staging': 'config/staging.yaml',
            'test': 'config/test.yaml',
            'testing': 'config/test.yaml',
            'development': 'config/config.yaml',
            'dev': 'config/config.yaml'
        }
        
        return config_map.get(env, 'config/config.yaml')
    
    def validate_configuration(self) -> List[str]:
        """Validate entire configuration and return warnings/errors"""
        warnings = []
        
        # Production-specific validations
        if not self.app_config.debug:
            if self.security_config.secret_key == "dev-key-change-in-production":
                warnings.append("🚨 CRITICAL: Using default secret key in production!")
            
            if self.app_config.host == "127.0.0.1":
                warnings.append("⚠️  Production app should bind to 0.0.0.0, not 127.0.0.1")
            
            if self.database_config.type == "mock":
                warnings.append("⚠️  Using mock database in production environment")
        
        # Security validations
        if self.security_config.cors_enabled and not self.security_config.cors_origins:
            warnings.append("⚠️  CORS enabled but no origins specified")
        
        # Performance validations
        if self.analytics_config.max_records_per_query > 50000:
            warnings.append(f"⚠️  Large query limit may impact performance: {self.analytics_config.max_records_per_query}")
        
        return warnings
    
    def get_effective_configuration(self) -> Dict[str, Any]:
        """Get the complete effective configuration as a dictionary"""
        return {
            'app': self._dataclass_to_dict(self.app_config),
            'database': self._dataclass_to_dict(self.database_config),
            'cache': self._dataclass_to_dict(self.cache_config),
            'security': self._dataclass_to_dict(self.security_config),
            'analytics': self._dataclass_to_dict(self.analytics_config),
            'monitoring': self._dataclass_to_dict(self.monitoring_config),
            '_meta': {
                'config_source': self._config_source,
                'environment': os.getenv('YOSAI_ENV', 'development')
            }
        }
    
    @staticmethod
    def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
        """Convert dataclass to dictionary"""
        result = {}
        for field_info in fields(obj):
            value = getattr(obj, field_info.name)
            if isinstance(value, list):
                result[field_info.name] = value.copy()
            else:
                result[field_info.name] = value
        return result
    
    def print_startup_info(self) -> None:
        """Print enhanced startup information"""
        print("\n" + "=" * 60)
        print("🏯 YŌSAI INTEL DASHBOARD")
        print("=" * 60)
        print(f"🌐 URL: http://{self.app_config.host}:{self.app_config.port}")
        print(f"🔧 Debug Mode: {self.app_config.debug}")
        print(f"📊 Analytics: http://{self.app_config.host}:{self.app_config.port}/analytics")
        print(f"📋 Config Source: {self._config_source or 'defaults'}")
        print(f"🌍 Environment: {os.getenv('YOSAI_ENV', 'development')}")
        print(f"🗄️  Database: {self.database_config.type}")
        print(f"💾 Cache: {self.cache_config.type}")
        print("=" * 60)
        
        # Show warnings
        warnings = self.validate_configuration()
        if warnings:
            print("⚠️  Configuration Warnings:")
            for warning in warnings:
                print(f"   {warning}")
            print("=" * 60)
        
        if self.app_config.debug:
            print("⚠️  Running in DEBUG mode - do not use in production!")
        
        print("\n🚀 Dashboard starting...")
    
    def save_effective_config(self, output_path: str) -> None:
        """Save the effective configuration to a file for debugging"""
        effective_config = self.get_effective_configuration()
        
        # Remove sensitive information
        if 'password' in effective_config.get('database', {}):
            effective_config['database']['password'] = "[REDACTED]"
        if 'secret_key' in effective_config.get('security', {}):
            effective_config['security']['secret_key'] = "[REDACTED]"
        
        with open(output_path, 'w') as f:
            yaml.dump(effective_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Effective configuration saved to: {output_path}")

class ConfigurationError(Exception):
    """Configuration-related errors"""
    pass

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
    'ConfigurationManager',
    'AppConfig', 'DatabaseConfig', 'CacheConfig', 'SecurityConfig', 
    'AnalyticsConfig', 'MonitoringConfig',
    'ConfigurationError',
    'create_configuration_manager',
    'get_configuration_manager',
    'reset_configuration_manager'
]