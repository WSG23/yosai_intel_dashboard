"""
YAML Configuration Management System  
Single source of truth for all configuration
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import yaml, provide fallback if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("Warning: PyYAML not installed. Install with: pip install pyyaml")
    YAML_AVAILABLE = False
    yaml = None

@dataclass
class AppConfig:
    """Application configuration with validation"""
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8050
    title: str = "Y\u014dsai Intel Dashboard"
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
class CacheConfig:
    """Cache configuration"""
    type: str = "memory"
    host: str = "localhost"
    port: int = 6379

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = "dev-key-change-in-production"
    session_timeout_minutes: int = 60
    max_file_size_mb: int = 100

@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    enabled: bool = True
    cache_ttl_seconds: int = 300

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    metrics_port: int = 9090

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class ConfigurationManager:
    """Main configuration manager - single source of truth"""
    
    def __init__(self):
        self.app_config = AppConfig()
        self.database_config = DatabaseConfig()
        self.cache_config = CacheConfig()
        self.security_config = SecurityConfig()
        self.analytics_config = AnalyticsConfig()
        self.monitoring_config = MonitoringConfig()
        self.logging_config = LoggingConfig()
        self._loaded_files: List[str] = []
    
    def load_configuration(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML file with environment overrides"""
        # Auto-detect config file if not specified
        if not config_path:
            env = os.getenv('YOSAI_ENV', 'development')
            config_path = f'config/{env}.yaml'
        
        # Load YAML if file exists and PyYAML is available
        if YAML_AVAILABLE and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                
                # Update configurations
                if 'app' in data:
                    self.app_config = AppConfig(**data['app'])
                if 'database' in data:
                    self.database_config = DatabaseConfig(**data['database'])
                if 'cache' in data:
                    self.cache_config = CacheConfig(**data['cache'])
                if 'security' in data:
                    self.security_config = SecurityConfig(**data['security'])
                if 'analytics' in data:
                    self.analytics_config = AnalyticsConfig(**data['analytics'])
                if 'monitoring' in data:
                    self.monitoring_config = MonitoringConfig(**data['monitoring'])
                if 'logging' in data:
                    self.logging_config = LoggingConfig(**data['logging'])
                
                self._loaded_files.append(config_path)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load {config_path}: {e}")
        
        # Apply environment variable overrides
        self._apply_env_overrides()
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        env_mappings = {
            "DB_HOST": ("database_config", "host"),
            "DB_PORT": ("database_config", "port"),
            "DB_USER": ("database_config", "username"),
            "DB_PASSWORD": ("database_config", "password"),
            "DB_NAME": ("database_config", "database"),
            "DB_TYPE": ("database_config", "type"),
            "SECRET_KEY": ("security_config", "secret_key"),
            "DEBUG": ("app_config", "debug"),
            "HOST": ("app_config", "host"),
            "PORT": ("app_config", "port"),
        }
        
        for env_var, (config_obj, field) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                obj = getattr(self, config_obj)
                current_type = type(getattr(obj, field))
                
                # Type conversion
                if current_type == bool:
                    value = value.lower() in ("true", "1", "yes", "on")
                elif current_type == int:
                    value = int(value)
                
                setattr(obj, field, value)

# Global singleton
_config_manager: Optional[ConfigurationManager] = None

def get_configuration_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
        _config_manager.load_configuration()
    return _config_manager

# Export all
__all__ = [
    "ConfigurationManager",
    "get_configuration_manager",
    "AppConfig",
    "DatabaseConfig", 
    "CacheConfig",
    "SecurityConfig",
    "AnalyticsConfig",
    "MonitoringConfig",
    "LoggingConfig"
]
