#!/usr/bin/env python3
"""
YAML Configuration Utilities
============================

Utility functions and classes for YAML configuration management.
Includes validation, environment variable handling, template generation, and more.

Author: Assistant
Python Version: 3.8+
"""

import os
import re
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import subprocess


@dataclass
class EnvironmentVariable:
    """Represents an environment variable with metadata"""
    name: str
    default_value: Optional[str] = None
    description: str = ""
    required: bool = True
    sensitive: bool = False
    validation_pattern: Optional[str] = None
    
    def is_valid(self, value: str) -> bool:
        """Check if value is valid for this environment variable"""
        if self.validation_pattern:
            return bool(re.match(self.validation_pattern, value))
        return True
    
    def __str__(self) -> str:
        return f"{self.name}{'*' if self.sensitive else ''}"


class EnvironmentVariableExtractor:
    """Extracts and analyzes environment variables from YAML configurations"""
    
    def __init__(self):
        self.env_var_pattern = re.compile(r'\$\{([^}]+)\}')
        self.logger = logging.getLogger(__name__)
        
        # Known sensitive patterns
        self.sensitive_patterns = [
            r'.*secret.*', r'.*password.*', r'.*token.*', r'.*key.*',
            r'.*auth.*', r'.*credential.*', r'.*private.*'
        ]
    
    def extract_from_config(self, config_data: Dict[str, Any]) -> List[EnvironmentVariable]:
        """Extract environment variables from configuration data"""
        env_vars = {}
        
        def extract_recursive(data: Any, path: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    extract_recursive(value, current_path)
            elif isinstance(data, str):
                matches = self.env_var_pattern.findall(data)
                for match in matches:
                    var_info = self._parse_env_var(match, path)
                    if var_info.name not in env_vars:
                        env_vars[var_info.name] = var_info
                    else:
                        # Merge information
                        existing = env_vars[var_info.name]
                        if not existing.default_value and var_info.default_value:
                            existing.default_value = var_info.default_value
                        if not existing.required and var_info.required:
                            existing.required = var_info.required
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    extract_recursive(item, f"{path}[{i}]")
        
        extract_recursive(config_data)
        return list(env_vars.values())
    
    def _parse_env_var(self, var_string: str, context_path: str) -> EnvironmentVariable:
        """Parse environment variable string like 'VAR:default' or 'VAR'"""
        if ':' in var_string:
            name, default = var_string.split(':', 1)
            required = False
        else:
            name = var_string
            default = None
            required = True
        
        # Check if variable name suggests sensitive data
        sensitive = any(re.match(pattern, name.lower()) for pattern in self.sensitive_patterns)
        
        # Generate description based on context
        description = f"Used in {context_path}"
        
        return EnvironmentVariable(
            name=name,
            default_value=default,
            description=description,
            required=required,
            sensitive=sensitive
        )
    
    def extract_from_file(self, file_path: str) -> List[EnvironmentVariable]:
        """Extract environment variables from a YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substitute environment variables to prevent parsing errors
            substituted_content = self._substitute_env_vars_for_parsing(content)
            config_data = yaml.safe_load(substituted_content) or {}
            
            return self.extract_from_config(config_data)
        
        except Exception as e:
            self.logger.error(f"Failed to extract from {file_path}: {e}")
            return []
    
    def _substitute_env_vars_for_parsing(self, content: str) -> str:
        """Substitute environment variables with dummy values for parsing"""
        def replace_env_var(match):
            var_expr = match.group(1)
            if ':' in var_expr:
                name, default = var_expr.split(':', 1)
                return default
            else:
                return f"dummy_value_for_{var_expr}"
        
        return self.env_var_pattern.sub(replace_env_var, content)
    
    def generate_env_file(self, env_vars: List[EnvironmentVariable], 
                         format: str = 'dotenv') -> str:
        """Generate environment file from environment variables"""
        if format == 'dotenv':
            return self._generate_dotenv(env_vars)
        elif format == 'docker':
            return self._generate_docker_env(env_vars)
        elif format == 'k8s':
            return self._generate_k8s_configmap(env_vars)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_dotenv(self, env_vars: List[EnvironmentVariable]) -> str:
        """Generate .env file format"""
        lines = []
        lines.append("# Environment variables for YAML configuration")
        lines.append(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Group by sensitivity
        regular_vars = [v for v in env_vars if not v.sensitive]
        sensitive_vars = [v for v in env_vars if v.sensitive]
        
        if regular_vars:
            lines.append("# Regular configuration variables")
            for var in sorted(regular_vars, key=lambda x: x.name):
                lines.append(f"# {var.description}")
                value = var.default_value if var.default_value else "CHANGE_ME"
                lines.append(f"{var.name}={value}")
                lines.append("")
        
        if sensitive_vars:
            lines.append("# Sensitive variables - CHANGE THESE VALUES!")
            for var in sorted(sensitive_vars, key=lambda x: x.name):
                lines.append(f"# {var.description}")
                value = var.default_value if var.default_value else "CHANGE_ME_SECURE_VALUE"
                lines.append(f"{var.name}={value}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_docker_env(self, env_vars: List[EnvironmentVariable]) -> str:
        """Generate Docker environment file format"""
        lines = []
        for var in env_vars:
            value = var.default_value if var.default_value else "CHANGE_ME"
            lines.append(f"{var.name}={value}")
        
        return "\n".join(lines)
    
    def _generate_k8s_configmap(self, env_vars: List[EnvironmentVariable]) -> str:
        """Generate Kubernetes ConfigMap YAML"""
        # Separate regular and sensitive vars
        regular_vars = [v for v in env_vars if not v.sensitive]
        sensitive_vars = [v for v in env_vars if v.sensitive]
        
        yaml_content = []
        
        if regular_vars:
            configmap = {
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': {
                    'name': 'app-config',
                    'labels': {
                        'app': 'yosai-dashboard'
                    }
                },
                'data': {}
            }
            
            for var in regular_vars:
                value = var.default_value if var.default_value else "CHANGE_ME"
                configmap['data'][var.name] = value
            
            yaml_content.append(yaml.dump(configmap, default_flow_style=False))
        
        if sensitive_vars:
            yaml_content.append("---")
            secret = {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'name': 'app-secrets',
                    'labels': {
                        'app': 'yosai-dashboard'
                    }
                },
                'type': 'Opaque',
                'stringData': {}
            }
            
            for var in sensitive_vars:
                value = var.default_value if var.default_value else "CHANGE_ME_SECURE"
                secret['stringData'][var.name] = value
            
            yaml_content.append(yaml.dump(secret, default_flow_style=False))
        
        return "\n".join(yaml_content)


class ConfigurationValidator:
    """Validates YAML configurations against schemas and best practices"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define expected configuration schema
        self.schema = {
            'app': {
                'required': ['debug', 'host', 'port'],
                'optional': ['title', 'timezone', 'log_level', 'enable_profiling']
            },
            'database': {
                'required': ['type'],
                'optional': ['host', 'port', 'database', 'username', 'password', 'pool_size']
            },
            'cache': {
                'required': ['type'],
                'optional': ['host', 'port', 'timeout_seconds', 'max_memory_mb']
            },
            'security': {
                'required': ['secret_key'],
                'optional': ['session_timeout_minutes', 'cors_enabled', 'cors_origins']
            },
            'analytics': {
                'required': [],
                'optional': ['cache_timeout_seconds', 'max_records_per_query', 'enable_real_time']
            },
            'monitoring': {
                'required': [],
                'optional': ['health_check_enabled', 'metrics_enabled', 'error_reporting_enabled']
            }
        }
    
    def validate_structure(self, config_data: Dict[str, Any]) -> List[str]:
        """Validate configuration structure against schema"""
        errors = []
        
        for section_name, section_schema in self.schema.items():
            if section_name not in config_data:
                errors.append(f"Missing required section: {section_name}")
                continue
            
            section_data = config_data[section_name]
            if not isinstance(section_data, dict):
                errors.append(f"Section {section_name} must be a dictionary")
                continue
            
            # Check required fields
            for required_field in section_schema['required']:
                if required_field not in section_data:
                    errors.append(f"Missing required field: {section_name}.{required_field}")
        
        return errors
    
    def validate_types(self, config_data: Dict[str, Any]) -> List[str]:
        """Validate data types in configuration"""
        errors = []
        
        type_checks = {
            ('app', 'debug'): bool,
            ('app', 'port'): (int, str),  # Allow string for env vars
            ('database', 'port'): (int, str),
            ('database', 'pool_size'): (int, str),
            ('cache', 'timeout_seconds'): (int, str),
            ('security', 'cors_enabled'): bool,
            ('security', 'cors_origins'): list,
            ('analytics', 'enable_real_time'): bool,
            ('monitoring', 'health_check_enabled'): bool
        }
        
        for (section, field), expected_type in type_checks.items():
            if section in config_data and field in config_data[section]:
                value = config_data[section][field]
                if not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {section}.{field}: expected {expected_type}, got {type(value)}")
        
        return errors
    
    def validate_values(self, config_data: Dict[str, Any]) -> List[str]:
        """Validate specific values in configuration"""
        errors = []
        
        # Port range validation
        for section_name in ['app', 'database', 'cache']:
            if section_name in config_data:
                section = config_data[section_name]
                if 'port' in section and isinstance(section['port'], int):
                    port = section['port']
                    if not (1 <= port <= 65535):
                        errors.append(f"Invalid port in {section_name}: {port} (must be 1-65535)")
        
        # Database type validation
        if 'database' in config_data:
            db_type = config_data['database'].get('type')
            valid_types = ['postgresql', 'mysql', 'sqlite', 'mock']
            if db_type and db_type not in valid_types:
                errors.append(f"Invalid database type: {db_type} (must be one of {valid_types})")
        
        # Cache type validation
        if 'cache' in config_data:
            cache_type = config_data['cache'].get('type')
            valid_types = ['redis', 'memory', 'memcached']
            if cache_type and cache_type not in valid_types:
                errors.append(f"Invalid cache type: {cache_type} (must be one of {valid_types})")
        
        # Log level validation
        if 'app' in config_data:
            log_level = config_data['app'].get('log_level')
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if log_level and log_level not in valid_levels:
                errors.append(f"Invalid log level: {log_level} (must be one of {valid_levels})")
        
        return errors
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a single configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML
            config_data = yaml.safe_load(content) or {}
            
            # Run validations
            structure_errors = self.validate_structure(config_data)
            type_errors = self.validate_types(config_data)
            value_errors = self.validate_values(config_data)
            
            all_errors = structure_errors + type_errors + value_errors
            
            return {
                'valid': len(all_errors) == 0,
                'errors': all_errors,
                'structure_errors': structure_errors,
                'type_errors': type_errors,
                'value_errors': value_errors,
                'config_data': config_data
            }
        
        except yaml.YAMLError as e:
            return {
                'valid': False,
                'errors': [f"YAML parsing error: {str(e)}"],
                'structure_errors': [],
                'type_errors': [],
                'value_errors': []
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'structure_errors': [],
                'type_errors': [],
                'value_errors': []
            }


class ConfigurationTemplate:
    """Generates configuration templates for different environments"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_development_config(self) -> Dict[str, Any]:
        """Generate development configuration template"""
        return {
            'app': {
                'debug': True,
                'host': '127.0.0.1',
                'port': 8050,
                'title': 'Yōsai Intel Dashboard - Development',
                'timezone': 'UTC',
                'log_level': 'INFO',
                'enable_profiling': False
            },
            'database': {
                'type': 'mock',
                'host': 'localhost',
                'port': 5432,
                'database': 'yosai_dev',
                'username': 'postgres',
                'password': '',
                'pool_size': 5,
                'connection_timeout': 30
            },
            'cache': {
                'type': 'memory',
                'timeout_seconds': 300,
                'max_memory_mb': 100,
                'key_prefix': 'yosai:dev:'
            },
            'security': {
                'secret_key': 'dev-key-change-in-production',
                'session_timeout_minutes': 120,
                'max_file_size_mb': 100,
                'cors_enabled': False,
                'cors_origins': []
            },
            'analytics': {
                'cache_timeout_seconds': 60,
                'max_records_per_query': 10000,
                'enable_real_time': True,
                'batch_size': 1000
            },
            'monitoring': {
                'health_check_enabled': True,
                'metrics_enabled': True,
                'performance_monitoring': False,
                'error_reporting_enabled': False
            }
        }
    
    def generate_production_config(self) -> Dict[str, Any]:
        """Generate production configuration template"""
        return {
            'app': {
                'debug': False,
                'host': '0.0.0.0',
                'port': '${PORT:8050}',
                'title': 'Yōsai Intel Dashboard - Production',
                'timezone': '${TIMEZONE:UTC}',
                'log_level': '${LOG_LEVEL:WARNING}',
                'enable_profiling': '${ENABLE_PROFILING:false}'
            },
            'database': {
                'type': 'postgresql',
                'host': '${DB_HOST}',
                'port': '${DB_PORT:5432}',
                'database': '${DB_NAME}',
                'username': '${DB_USER}',
                'password': '${DB_PASSWORD}',
                'pool_size': '${DB_POOL_SIZE:20}',
                'ssl_mode': '${DB_SSL_MODE:require}',
                'connection_timeout': '${DB_TIMEOUT:30}'
            },
            'cache': {
                'type': 'redis',
                'host': '${REDIS_HOST}',
                'port': '${REDIS_PORT:6379}',
                'database': '${REDIS_DB:0}',
                'timeout_seconds': '${CACHE_TIMEOUT:600}',
                'key_prefix': '${CACHE_PREFIX:yosai:prod:}',
                'compression_enabled': '${CACHE_COMPRESSION:true}'
            },
            'security': {
                'secret_key': '${SECRET_KEY}',
                'session_timeout_minutes': '${SESSION_TIMEOUT:30}',
                'max_file_size_mb': '${MAX_FILE_SIZE:50}',
                'cors_enabled': '${CORS_ENABLED:true}',
                'cors_origins': ['${FRONTEND_URL}', '${API_URL}'],
                'rate_limiting_enabled': '${RATE_LIMITING:true}',
                'rate_limit_per_minute': '${RATE_LIMIT:120}'
            },
            'analytics': {
                'cache_timeout_seconds': '${ANALYTICS_CACHE_TIMEOUT:600}',
                'max_records_per_query': '${MAX_QUERY_RECORDS:50000}',
                'enable_real_time': '${ENABLE_REAL_TIME:true}',
                'batch_size': '${BATCH_SIZE:5000}',
                'anomaly_detection_enabled': '${ENABLE_ANOMALY_DETECTION:true}'
            },
            'monitoring': {
                'health_check_enabled': True,
                'metrics_enabled': True,
                'performance_monitoring': '${ENABLE_PERFORMANCE_MONITORING:true}',
                'error_reporting_enabled': '${ENABLE_ERROR_REPORTING:true}',
                'sentry_dsn': '${SENTRY_DSN}',
                'log_retention_days': '${LOG_RETENTION_DAYS:90}'
            }
        }
    
    def generate_staging_config(self) -> Dict[str, Any]:
        """Generate staging configuration template"""
        prod_config = self.generate_production_config()
        
        # Modify for staging specifics
        staging_overrides = {
            'app': {
                'title': 'Yōsai Intel Dashboard - Staging',
                'log_level': '${LOG_LEVEL:INFO}',
                'enable_profiling': '${ENABLE_PROFILING:true}'
            },
            'database': {
                'host': '${DB_HOST:staging-db.internal}',
                'database': '${DB_NAME:yosai_staging}',
                'pool_size': '${DB_POOL_SIZE:10}'
            },
            'cache': {
                'host': '${REDIS_HOST:staging-redis.internal}',
                'database': '${REDIS_DB:1}',
                'key_prefix': '${CACHE_PREFIX:yosai:staging:}'
            },
            'security': {
                'session_timeout_minutes': '${SESSION_TIMEOUT:60}',
                'max_file_size_mb': '${MAX_FILE_SIZE:100}',
                'rate_limit_per_minute': '${RATE_LIMIT:200}'
            },
            'analytics': {
                'cache_timeout_seconds': '${ANALYTICS_CACHE_TIMEOUT:300}',
                'max_records_per_query': '${MAX_QUERY_RECORDS:25000}'
            }
        }
        
        # Deep merge staging overrides
        for section, overrides in staging_overrides.items():
            if section in prod_config:
                prod_config[section].update(overrides)
        
        return prod_config
    
    def generate_test_config(self) -> Dict[str, Any]:
        """Generate test configuration template"""
        return {
            'app': {
                'debug': True,
                'host': '127.0.0.1',
                'port': 8051,
                'title': 'Yōsai Intel Dashboard - Test',
                'log_level': 'DEBUG',
                'enable_profiling': False
            },
            'database': {
                'type': 'mock',
                'connection_timeout': 5,
                'retry_attempts': 1
            },
            'cache': {
                'type': 'memory',
                'timeout_seconds': 1,
                'max_memory_mb': 10,
                'key_prefix': 'yosai:test:'
            },
            'security': {
                'secret_key': 'test-secret-key-for-testing-only',
                'session_timeout_minutes': 5,
                'max_file_size_mb': 10,
                'rate_limiting_enabled': False
            },
            'analytics': {
                'cache_timeout_seconds': 1,
                'max_records_per_query': 100,
                'enable_real_time': False,
                'batch_size': 10,
                'anomaly_detection_enabled': False
            },
            'monitoring': {
                'health_check_enabled': False,
                'metrics_enabled': False,
                'performance_monitoring': False,
                'error_reporting_enabled': False,
                'log_retention_days': 1
            }
        }
    
    def save_template(self, config: Dict[str, Any], file_path: str, 
                     add_comments: bool = True) -> None:
        """Save configuration template to file with optional comments"""
        if add_comments:
            yaml_content = self._add_comments_to_yaml(config, file_path)
        else:
            yaml_content = yaml.dump(config, default_flow_style=False, 
                                   allow_unicode=True, sort_keys=False)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
    
    def _add_comments_to_yaml(self, config: Dict[str, Any], file_path: str) -> str:
        """Add helpful comments to YAML configuration"""
        lines = []
        
        # Determine environment from filename
        filename = Path(file_path).name.lower()
        if 'production' in filename or 'prod' in filename:
            env = 'production'
        elif 'staging' in filename:
            env = 'staging'
        elif 'test' in filename:
            env = 'test'
        else:
            env = 'development'
        
        # Header comment
        lines.append(f"# {Path(file_path).name} - {env.title()} Environment Configuration")
        lines.append("# Yōsai Intel Dashboard")
        lines.append("#")
        if env == 'production':
            lines.append("# Production configuration with environment variable substitution")
            lines.append("# Ensure all required environment variables are set before deployment")
        elif env == 'staging':
            lines.append("# Staging configuration for testing production-like settings")
        elif env == 'test':
            lines.append("# Test configuration optimized for automated testing")
        else:
            lines.append("# Development configuration with sensible defaults")
        lines.append("")
        
        # Convert to YAML and add section comments
        yaml_content = yaml.dump(config, default_flow_style=False, 
                               allow_unicode=True, sort_keys=False)
        
        yaml_lines = yaml_content.split('\n')
        in_section = None
        
        for line in yaml_lines:
            # Check if this is a top-level section
            if line and not line.startswith(' ') and ':' in line:
                section = line.split(':')[0].strip()
                if section in ['app', 'database', 'cache', 'security', 'analytics', 'monitoring']:
                    # Add section comment
                    lines.append(f"# ===== {section.upper()} CONFIGURATION =====")
                    in_section = section
            
            lines.append(line)
        
        return '\n'.join(lines)


class ConfigurationDiffer:
    """Compares configurations and identifies differences"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compare_configs(self, config1: Dict[str, Any], config2: Dict[str, Any], 
                       name1: str = "config1", name2: str = "config2") -> Dict[str, Any]:
        """Compare two configurations and return differences"""
        differences = {
            'added': {},
            'removed': {},
            'changed': {},
            'unchanged': {},
            'summary': {
                'total_changes': 0,
                'sections_affected': set()
            }
        }
        
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            if key not in config1:
                differences['added'][key] = config2[key]
                differences['summary']['total_changes'] += 1
                differences['summary']['sections_affected'].add(key)
            elif key not in config2:
                differences['removed'][key] = config1[key]
                differences['summary']['total_changes'] += 1
                differences['summary']['sections_affected'].add(key)
            else:
                # Compare section contents
                section_diff = self._compare_sections(config1[key], config2[key], key)
                if section_diff['has_changes']:
                    differences['changed'][key] = section_diff
                    differences['summary']['total_changes'] += section_diff['change_count']
                    differences['summary']['sections_affected'].add(key)
                else:
                    differences['unchanged'][key] = config1[key]
        
        differences['summary']['sections_affected'] = list(differences['summary']['sections_affected'])
        
        return differences
    
    def _compare_sections(self, section1: Any, section2: Any, section_name: str) -> Dict[str, Any]:
        """Compare individual sections"""
        if not isinstance(section1, dict) or not isinstance(section2, dict):
            return {
                'has_changes': section1 != section2,
                'change_count': 1 if section1 != section2 else 0,
                'old_value': section1,
                'new_value': section2
            }
        
        diff = {
            'has_changes': False,
            'change_count': 0,
            'added': {},
            'removed': {},
            'changed': {},
            'unchanged': {}
        }
        
        all_keys = set(section1.keys()) | set(section2.keys())
        
        for key in all_keys:
            if key not in section1:
                diff['added'][key] = section2[key]
                diff['has_changes'] = True
                diff['change_count'] += 1
            elif key not in section2:
                diff['removed'][key] = section1[key]
                diff['has_changes'] = True
                diff['change_count'] += 1
            elif section1[key] != section2[key]:
                diff['changed'][key] = {
                    'old': section1[key],
                    'new': section2[key]
                }
                diff['has_changes'] = True
                diff['change_count'] += 1
            else:
                diff['unchanged'][key] = section1[key]
        
        return diff
    
    def compare_files(self, file1: str, file2: str) -> Dict[str, Any]:
        """Compare two configuration files"""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                config1 = yaml.safe_load(f) or {}
            
            with open(file2, 'r', encoding='utf-8') as f:
                config2 = yaml.safe_load(f) or {}
            
            return self.compare_configs(config1, config2, 
                                      Path(file1).name, Path(file2).name)
        
        except Exception as e:
            self.logger.error(f"Failed to compare files: {e}")
            return {'error': str(e)}
    
    def generate_diff_report(self, differences: Dict[str, Any]) -> str:
        """Generate a human-readable diff report"""
        if 'error' in differences:
            return f"Error: {differences['error']}"
        
        lines = []
        lines.append("Configuration Comparison Report")
        lines.append("=" * 40)
        lines.append("")
        
        summary = differences['summary']
        lines.append(f"Total Changes: {summary['total_changes']}")
        lines.append(f"Sections Affected: {', '.join(summary['sections_affected'])}")
        lines.append("")
        
        # Added sections
        if differences['added']:
            lines.append("Added Sections:")
            for section, content in differences['added'].items():
                lines.append(f"  + {section}")
                lines.append("    " + yaml.dump(content, default_flow_style=False).replace('\n', '\n    '))
        
        # Removed sections
        if differences['removed']:
            lines.append("Removed Sections:")
            for section, content in differences['removed'].items():
                lines.append(f"  - {section}")
        
        # Changed sections
        if differences['changed']:
            lines.append("Changed Sections:")
            for section, changes in differences['changed'].items():
                lines.append(f"  ~ {section}:")
                
                if 'added' in changes:
                    for key, value in changes['added'].items():
                        lines.append(f"    + {key}: {value}")
                
                if 'removed' in changes:
                    for key, value in changes['removed'].items():
                        lines.append(f"    - {key}: {value}")
                
                if 'changed' in changes:
                    for key, change in changes['changed'].items():
                        lines.append(f"    ~ {key}: {change['old']} -> {change['new']}")
        
        return '\n'.join(lines)


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YAML Configuration Utilities")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract environment variables command
    extract_parser = subparsers.add_parser('extract-env', help='Extract environment variables')
    extract_parser.add_argument('config_file', help='Configuration file to analyze')
    extract_parser.add_argument('--format', choices=['dotenv', 'docker', 'k8s'], 
                               default='dotenv', help='Output format')
    extract_parser.add_argument('--output', '-o', help='Output file')
    
    # Validate configuration command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('config_file', help='Configuration file to validate')
    
    # Generate template command
    template_parser = subparsers.add_parser('template', help='Generate configuration template')
    template_parser.add_argument('environment', choices=['dev', 'staging', 'prod', 'test'],
                                help='Environment type')
    template_parser.add_argument('--output', '-o', required=True, help='Output file')
    template_parser.add_argument('--no-comments', action='store_true', 
                                help='Skip adding comments')
    
    # Compare configurations command
    compare_parser = subparsers.add_parser('compare', help='Compare configurations')
    compare_parser.add_argument('file1', help='First configuration file')
    compare_parser.add_argument('file2', help='Second configuration file')
    compare_parser.add_argument('--output', '-o', help='Output report file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'extract-env':
            extractor = EnvironmentVariableExtractor()
            env_vars = extractor.extract_from_file(args.config_file)
            env_content = extractor.generate_env_file(env_vars, args.format)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(env_content)
                print(f"Environment variables written to {args.output}")
            else:
                print(env_content)
        
        elif args.command == 'validate':
            validator = ConfigurationValidator()
            result = validator.validate_file(args.config_file)
            
            if result['valid']:
                print(f"✅ Configuration {args.config_file} is valid")
            else:
                print(f"❌ Configuration {args.config_file} has errors:")
                for error in result['errors']:
                    print(f"  - {error}")
                return 1
        
        elif args.command == 'template':
            template_gen = ConfigurationTemplate()
            
            if args.environment == 'dev':
                config = template_gen.generate_development_config()
            elif args.environment == 'staging':
                config = template_gen.generate_staging_config()
            elif args.environment == 'prod':
                config = template_gen.generate_production_config()
            elif args.environment == 'test':
                config = template_gen.generate_test_config()
            
            template_gen.save_template(config, args.output, not args.no_comments)
            print(f"Configuration template written to {args.output}")
        
        elif args.command == 'compare':
            differ = ConfigurationDiffer()
            differences = differ.compare_files(args.file1, args.file2)
            report = differ.generate_diff_report(differences)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Comparison report written to {args.output}")
            else:
                print(report)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())