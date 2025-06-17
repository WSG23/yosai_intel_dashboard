#!/usr/bin/env python3
"""
YAML Configuration Comprehensive Review Tool
===========================================

A modular tool for analyzing YAML configuration systems.
Provides detailed analysis, validation, and recommendations.

Author: Assistant
Python Version: 3.8+
"""

import os
import sys
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import re


class SeverityLevel(Enum):
    """Severity levels for configuration issues"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ConfigurationIssueType(Enum):
    """Types of configuration issues"""
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    MAINTAINABILITY = "MAINTAINABILITY"
    VALIDATION = "VALIDATION"
    STRUCTURE = "STRUCTURE"
    ENVIRONMENT = "ENVIRONMENT"


@dataclass
class ConfigurationIssue:
    """Represents a configuration issue found during analysis"""
    type: ConfigurationIssueType
    severity: SeverityLevel
    title: str
    description: str
    location: str
    current_value: Any = None
    recommended_value: Any = None
    fix_suggestion: str = ""
    
    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.title} in {self.location}"


@dataclass
class ConfigurationMetrics:
    """Metrics about the configuration system"""
    total_files: int = 0
    total_environments: int = 0
    total_sections: int = 0
    environment_variables_used: int = 0
    security_issues: int = 0
    performance_issues: int = 0
    maintainability_score: float = 0.0
    complexity_score: float = 0.0


# Base analyzer interface
class ConfigurationAnalyzer(ABC):
    """Base class for configuration analyzers"""
    
    @abstractmethod
    def analyze(self, config_data: Dict[str, Any], context: Dict[str, Any]) -> List[ConfigurationIssue]:
        """Analyze configuration and return issues"""
        pass


class SecurityAnalyzer(ConfigurationAnalyzer):
    """Analyzes security aspects of YAML configuration"""
    
    def __init__(self):
        self.sensitive_keys = {
            'secret_key', 'password', 'token', 'api_key', 'private_key',
            'auth_token', 'access_key', 'session_secret', 'encryption_key'
        }
        
        self.insecure_defaults = {
            'dev-key-change-in-production': 'Default development secret key',
            'password': 'Default password',
            '123456': 'Weak password',
            'admin': 'Default admin credentials'
        }
    
    def analyze(self, config_data: Dict[str, Any], context: Dict[str, Any]) -> List[ConfigurationIssue]:
        """Analyze security configuration"""
        issues = []
        file_path = context.get('file_path', 'unknown')
        environment = context.get('environment', 'unknown')
        
        # Check for hardcoded secrets
        issues.extend(self._check_hardcoded_secrets(config_data, file_path))
        
        # Check for insecure defaults
        issues.extend(self._check_insecure_defaults(config_data, file_path))
        
        # Check production-specific security
        if environment == 'production':
            issues.extend(self._check_production_security(config_data, file_path))
        
        # Check CORS configuration
        issues.extend(self._check_cors_configuration(config_data, file_path))
        
        return issues
    
    def _check_hardcoded_secrets(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check for hardcoded secrets in configuration"""
        issues = []
        
        def check_recursive(data: Any, path: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Check if key suggests sensitive data
                    if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
                        if isinstance(value, str) and not value.startswith('${'):
                            issues.append(ConfigurationIssue(
                                type=ConfigurationIssueType.SECURITY,
                                severity=SeverityLevel.HIGH,
                                title="Hardcoded Secret",
                                description=f"Sensitive key '{key}' contains hardcoded value",
                                location=f"{file_path}:{current_path}",
                                current_value="[REDACTED]",
                                recommended_value="${ENV_VAR}",
                                fix_suggestion="Use environment variable substitution"
                            ))
                    
                    check_recursive(value, current_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_recursive(item, f"{path}[{i}]")
        
        check_recursive(config_data)
        return issues
    
    def _check_insecure_defaults(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check for known insecure default values"""
        issues = []
        
        def check_recursive(data: Any, path: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, str) and value in self.insecure_defaults:
                        issues.append(ConfigurationIssue(
                            type=ConfigurationIssueType.SECURITY,
                            severity=SeverityLevel.CRITICAL,
                            title="Insecure Default Value",
                            description=self.insecure_defaults[value],
                            location=f"{file_path}:{current_path}",
                            current_value=value,
                            fix_suggestion="Change to secure value or use environment variable"
                        ))
                    
                    check_recursive(value, current_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_recursive(item, f"{path}[{i}]")
        
        check_recursive(config_data)
        return issues
    
    def _check_production_security(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check production-specific security settings"""
        issues = []
        
        # Check debug mode
        app_config = config_data.get('app', {})
        if app_config.get('debug', False):
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.SECURITY,
                severity=SeverityLevel.HIGH,
                title="Debug Mode in Production",
                description="Debug mode should be disabled in production",
                location=f"{file_path}:app.debug",
                current_value=True,
                recommended_value=False
            ))
        
        # Check host binding
        if app_config.get('host') == '127.0.0.1':
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.SECURITY,
                severity=SeverityLevel.MEDIUM,
                title="Localhost Binding in Production",
                description="Application bound to localhost only",
                location=f"{file_path}:app.host",
                current_value="127.0.0.1",
                recommended_value="0.0.0.0"
            ))
        
        return issues
    
    def _check_cors_configuration(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check CORS configuration security"""
        issues = []
        
        security_config = config_data.get('security', {})
        
        if security_config.get('cors_enabled'):
            cors_origins = security_config.get('cors_origins', [])
            
            # Check for wildcard CORS
            if '*' in cors_origins:
                issues.append(ConfigurationIssue(
                    type=ConfigurationIssueType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    title="Wildcard CORS Origin",
                    description="Using wildcard (*) in CORS origins is insecure",
                    location=f"{file_path}:security.cors_origins",
                    current_value=cors_origins,
                    fix_suggestion="Specify exact allowed origins"
                ))
        
        return issues


class PerformanceAnalyzer(ConfigurationAnalyzer):
    """Analyzes performance aspects of YAML configuration"""
    
    def analyze(self, config_data: Dict[str, Any], context: Dict[str, Any]) -> List[ConfigurationIssue]:
        """Analyze performance configuration"""
        issues = []
        file_path = context.get('file_path', 'unknown')
        
        # Check database configuration
        issues.extend(self._check_database_performance(config_data, file_path))
        
        # Check cache configuration
        issues.extend(self._check_cache_performance(config_data, file_path))
        
        # Check analytics configuration
        issues.extend(self._check_analytics_performance(config_data, file_path))
        
        return issues
    
    def _check_database_performance(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check database performance settings"""
        issues = []
        
        db_config = config_data.get('database', {})
        
        # Check connection pool size
        pool_size = db_config.get('pool_size', 5)
        if pool_size < 5:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.PERFORMANCE,
                severity=SeverityLevel.MEDIUM,
                title="Small Database Pool Size",
                description="Database pool size may be too small for production load",
                location=f"{file_path}:database.pool_size",
                current_value=pool_size,
                recommended_value="10-20 for production"
            ))
        
        # Check connection timeout
        timeout = db_config.get('connection_timeout', 30)
        if timeout > 60:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.PERFORMANCE,
                severity=SeverityLevel.LOW,
                title="Long Database Timeout",
                description="Long connection timeout may cause poor user experience",
                location=f"{file_path}:database.connection_timeout",
                current_value=timeout,
                recommended_value="30-60 seconds"
            ))
        
        return issues
    
    def _check_cache_performance(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check cache performance settings"""
        issues = []
        
        cache_config = config_data.get('cache', {})
        
        # Check cache timeout
        timeout = cache_config.get('timeout_seconds', 300)
        if timeout < 60:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.PERFORMANCE,
                severity=SeverityLevel.LOW,
                title="Short Cache Timeout",
                description="Very short cache timeout may reduce effectiveness",
                location=f"{file_path}:cache.timeout_seconds",
                current_value=timeout,
                recommended_value="300-600 seconds"
            ))
        
        # Check memory limit for memory cache
        if cache_config.get('type') == 'memory':
            max_memory = cache_config.get('max_memory_mb', 100)
            if max_memory < 50:
                issues.append(ConfigurationIssue(
                    type=ConfigurationIssueType.PERFORMANCE,
                    severity=SeverityLevel.MEDIUM,
                    title="Low Memory Cache Limit",
                    description="Memory cache limit may be too low",
                    location=f"{file_path}:cache.max_memory_mb",
                    current_value=max_memory,
                    recommended_value="100-500 MB"
                ))
        
        return issues
    
    def _check_analytics_performance(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check analytics performance settings"""
        issues = []
        
        analytics_config = config_data.get('analytics', {})
        
        # Check max records per query
        max_records = analytics_config.get('max_records_per_query', 10000)
        if max_records > 100000:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.PERFORMANCE,
                severity=SeverityLevel.HIGH,
                title="High Query Record Limit",
                description="Very high record limit may cause memory/performance issues",
                location=f"{file_path}:analytics.max_records_per_query",
                current_value=max_records,
                recommended_value="10000-50000"
            ))
        
        # Check batch size
        batch_size = analytics_config.get('batch_size', 1000)
        if batch_size > 10000:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.PERFORMANCE,
                severity=SeverityLevel.MEDIUM,
                title="Large Batch Size",
                description="Large batch size may cause memory issues",
                location=f"{file_path}:analytics.batch_size",
                current_value=batch_size,
                recommended_value="1000-5000"
            ))
        
        return issues


class MaintainabilityAnalyzer(ConfigurationAnalyzer):
    """Analyzes maintainability aspects of YAML configuration"""
    
    def analyze(self, config_data: Dict[str, Any], context: Dict[str, Any]) -> List[ConfigurationIssue]:
        """Analyze maintainability configuration"""
        issues = []
        file_path = context.get('file_path', 'unknown')
        
        # Check environment variable usage
        issues.extend(self._check_environment_variables(config_data, file_path))
        
        # Check configuration structure
        issues.extend(self._check_configuration_structure(config_data, file_path))
        
        # Check documentation
        issues.extend(self._check_documentation(config_data, file_path, context))
        
        return issues
    
    def _check_environment_variables(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check environment variable usage patterns"""
        issues = []
        env_var_pattern = re.compile(r'\$\{([^}]+)\}')
        
        def check_recursive(data: Any, path: str = ""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    check_recursive(value, current_path)
            elif isinstance(data, str):
                matches = env_var_pattern.findall(data)
                for match in matches:
                    # Check for missing default values
                    if ':' not in match:
                        issues.append(ConfigurationIssue(
                            type=ConfigurationIssueType.MAINTAINABILITY,
                            severity=SeverityLevel.MEDIUM,
                            title="Environment Variable Without Default",
                            description=f"Environment variable '{match}' has no default value",
                            location=f"{file_path}:{path}",
                            current_value=f"${{{match}}}",
                            recommended_value=f"${{{match}:default_value}}",
                            fix_suggestion="Add default value for better robustness"
                        ))
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    check_recursive(item, f"{path}[{i}]")
        
        check_recursive(config_data)
        return issues
    
    def _check_configuration_structure(self, config_data: Dict[str, Any], file_path: str) -> List[ConfigurationIssue]:
        """Check configuration structure and organization"""
        issues = []
        
        # Check for expected sections
        expected_sections = {'app', 'database', 'cache', 'security', 'analytics', 'monitoring'}
        actual_sections = set(config_data.keys())
        
        missing_sections = expected_sections - actual_sections
        if missing_sections:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.STRUCTURE,
                severity=SeverityLevel.LOW,
                title="Missing Configuration Sections",
                description=f"Missing sections: {', '.join(missing_sections)}",
                location=file_path,
                fix_suggestion="Add missing sections with appropriate defaults"
            ))
        
        # Check for unknown sections
        unknown_sections = actual_sections - expected_sections
        if unknown_sections:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.STRUCTURE,
                severity=SeverityLevel.INFO,
                title="Unknown Configuration Sections",
                description=f"Unknown sections: {', '.join(unknown_sections)}",
                location=file_path,
                fix_suggestion="Verify these sections are intentional"
            ))
        
        return issues
    
    def _check_documentation(self, config_data: Dict[str, Any], file_path: str, context: Dict[str, Any]) -> List[ConfigurationIssue]:
        """Check for configuration documentation"""
        issues = []
        
        # Check if file has comments (this would require parsing the raw YAML)
        raw_content = context.get('raw_content', '')
        if raw_content and '#' not in raw_content:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.MAINTAINABILITY,
                severity=SeverityLevel.LOW,
                title="No Documentation Comments",
                description="Configuration file lacks documentation comments",
                location=file_path,
                fix_suggestion="Add comments explaining configuration sections and values"
            ))
        
        return issues


class EnvironmentAnalyzer(ConfigurationAnalyzer):
    """Analyzes environment-specific configuration aspects"""
    
    def analyze(self, config_data: Dict[str, Any], context: Dict[str, Any]) -> List[ConfigurationIssue]:
        """Analyze environment-specific configuration"""
        issues = []
        file_path = context.get('file_path', 'unknown')
        environment = context.get('environment', 'unknown')
        
        # Check environment-specific settings
        issues.extend(self._check_environment_appropriateness(config_data, file_path, environment))
        
        # Check for environment consistency
        issues.extend(self._check_environment_consistency(config_data, file_path, environment))
        
        return issues
    
    def _check_environment_appropriateness(self, config_data: Dict[str, Any], file_path: str, environment: str) -> List[ConfigurationIssue]:
        """Check if settings are appropriate for the environment"""
        issues = []
        
        app_config = config_data.get('app', {})
        
        if environment == 'production':
            # Production-specific checks
            if app_config.get('enable_profiling', False):
                issues.append(ConfigurationIssue(
                    type=ConfigurationIssueType.ENVIRONMENT,
                    severity=SeverityLevel.MEDIUM,
                    title="Profiling Enabled in Production",
                    description="Performance profiling should typically be disabled in production",
                    location=f"{file_path}:app.enable_profiling",
                    current_value=True,
                    recommended_value=False
                ))
            
            if app_config.get('log_level', 'INFO') == 'DEBUG':
                issues.append(ConfigurationIssue(
                    type=ConfigurationIssueType.ENVIRONMENT,
                    severity=SeverityLevel.MEDIUM,
                    title="Debug Logging in Production",
                    description="Debug log level may impact performance and security",
                    location=f"{file_path}:app.log_level",
                    current_value="DEBUG",
                    recommended_value="WARNING or ERROR"
                ))
        
        elif environment == 'development':
            # Development-specific checks
            monitoring_config = config_data.get('monitoring', {})
            if monitoring_config.get('error_reporting_enabled', False):
                issues.append(ConfigurationIssue(
                    type=ConfigurationIssueType.ENVIRONMENT,
                    severity=SeverityLevel.INFO,
                    title="Error Reporting in Development",
                    description="Error reporting to external services may not be needed in development",
                    location=f"{file_path}:monitoring.error_reporting_enabled",
                    current_value=True,
                    fix_suggestion="Consider disabling for development environment"
                ))
        
        return issues
    
    def _check_environment_consistency(self, config_data: Dict[str, Any], file_path: str, environment: str) -> List[ConfigurationIssue]:
        """Check consistency within environment configuration"""
        issues = []
        
        # Check title consistency
        app_config = config_data.get('app', {})
        title = app_config.get('title', '')
        
        expected_env_in_title = environment.title()
        if environment != 'development' and expected_env_in_title not in title:
            issues.append(ConfigurationIssue(
                type=ConfigurationIssueType.ENVIRONMENT,
                severity=SeverityLevel.LOW,
                title="Environment Not in Title",
                description=f"Application title doesn't indicate {environment} environment",
                location=f"{file_path}:app.title",
                current_value=title,
                fix_suggestion=f"Include '{expected_env_in_title}' in title"
            ))
        
        return issues


class YAMLConfigurationReviewer:
    """Main class for comprehensive YAML configuration review"""
    
    def __init__(self):
        self.analyzers = [
            SecurityAnalyzer(),
            PerformanceAnalyzer(),
            MaintainabilityAnalyzer(),
            EnvironmentAnalyzer()
        ]
        self.logger = logging.getLogger(__name__)
    
    def review_configuration_system(self, config_directory: str) -> Dict[str, Any]:
        """Review entire configuration system"""
        config_path = Path(config_directory)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration directory not found: {config_directory}")
        
        review_results = {
            'summary': {},
            'files': {},
            'issues': [],
            'metrics': ConfigurationMetrics(),
            'recommendations': []
        }
        
        # Find all YAML files
        yaml_files = list(config_path.glob("*.yaml")) + list(config_path.glob("*.yml"))
        
        for yaml_file in yaml_files:
            file_results = self.review_configuration_file(str(yaml_file))
            review_results['files'][yaml_file.name] = file_results
            review_results['issues'].extend(file_results['issues'])
        
        # Calculate overall metrics
        review_results['metrics'] = self._calculate_metrics(review_results)
        
        # Generate recommendations
        review_results['recommendations'] = self._generate_recommendations(review_results)
        
        # Create summary
        review_results['summary'] = self._create_summary(review_results)
        
        return review_results
    
    def review_configuration_file(self, file_path: str) -> Dict[str, Any]:
        """Review a single configuration file"""
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Read and parse YAML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            config_data = yaml.safe_load(raw_content) or {}
        except yaml.YAMLError as e:
            return {
                'issues': [ConfigurationIssue(
                    type=ConfigurationIssueType.VALIDATION,
                    severity=SeverityLevel.CRITICAL,
                    title="YAML Parsing Error",
                    description=f"Failed to parse YAML: {str(e)}",
                    location=file_path
                )],
                'valid': False
            }
        
        # Determine environment from filename
        environment = self._determine_environment(file_path_obj.name)
        
        # Create analysis context
        context = {
            'file_path': file_path,
            'environment': environment,
            'raw_content': raw_content
        }
        
        # Run all analyzers
        all_issues = []
        for analyzer in self.analyzers:
            try:
                issues = analyzer.analyze(config_data, context)
                all_issues.extend(issues)
            except Exception as e:
                self.logger.error(f"Analyzer {analyzer.__class__.__name__} failed: {e}")
        
        return {
            'issues': all_issues,
            'environment': environment,
            'sections': list(config_data.keys()),
            'valid': True,
            'config_data': config_data
        }
    
    def _determine_environment(self, filename: str) -> str:
        """Determine environment from filename"""
        filename_lower = filename.lower()
        
        if 'production' in filename_lower or 'prod' in filename_lower:
            return 'production'
        elif 'staging' in filename_lower or 'stage' in filename_lower:
            return 'staging'
        elif 'test' in filename_lower:
            return 'test'
        elif 'development' in filename_lower or 'dev' in filename_lower:
            return 'development'
        else:
            return 'unknown'
    
    def _calculate_metrics(self, review_results: Dict[str, Any]) -> ConfigurationMetrics:
        """Calculate metrics from review results"""
        metrics = ConfigurationMetrics()
        
        metrics.total_files = len(review_results['files'])
        
        # Count environments
        environments = set()
        for file_data in review_results['files'].values():
            if file_data.get('environment'):
                environments.add(file_data['environment'])
        metrics.total_environments = len(environments)
        
        # Count sections
        sections = set()
        for file_data in review_results['files'].values():
            sections.update(file_data.get('sections', []))
        metrics.total_sections = len(sections)
        
        # Count issues by type
        for issue in review_results['issues']:
            if issue.type == ConfigurationIssueType.SECURITY:
                metrics.security_issues += 1
            elif issue.type == ConfigurationIssueType.PERFORMANCE:
                metrics.performance_issues += 1
        
        # Calculate environment variable usage
        env_var_count = 0
        for file_data in review_results['files'].values():
            if file_data.get('valid'):
                env_var_count += self._count_environment_variables(file_data.get('config_data', {}))
        metrics.environment_variables_used = env_var_count
        
        # Calculate scores (simplified)
        total_issues = len(review_results['issues'])
        critical_high_issues = len([i for i in review_results['issues'] 
                                  if i.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]])
        
        metrics.maintainability_score = max(0, 100 - (critical_high_issues * 10))
        metrics.complexity_score = min(100, metrics.total_sections * 5 + metrics.environment_variables_used * 2)
        
        return metrics
    
    def _count_environment_variables(self, config_data: Dict[str, Any]) -> int:
        """Count environment variables in configuration"""
        count = 0
        env_var_pattern = re.compile(r'\$\{[^}]+\}')
        
        def count_recursive(data: Any):
            nonlocal count
            if isinstance(data, dict):
                for value in data.values():
                    count_recursive(value)
            elif isinstance(data, str):
                count += len(env_var_pattern.findall(data))
            elif isinstance(data, list):
                for item in data:
                    count_recursive(item)
        
        count_recursive(config_data)
        return count
    
    def _generate_recommendations(self, review_results: Dict[str, Any]) -> List[str]:
        """Generate high-level recommendations"""
        recommendations = []
        
        metrics = review_results['metrics']
        issues = review_results['issues']
        
        # Security recommendations
        security_issues = [i for i in issues if i.type == ConfigurationIssueType.SECURITY]
        if security_issues:
            critical_security = [i for i in security_issues if i.severity == SeverityLevel.CRITICAL]
            if critical_security:
                recommendations.append(
                    f"🚨 URGENT: Address {len(critical_security)} critical security issues immediately"
                )
            recommendations.append(
                "Consider implementing a secrets management system (e.g., HashiCorp Vault, AWS Secrets Manager)"
            )
        
        # Performance recommendations
        performance_issues = [i for i in issues if i.type == ConfigurationIssueType.PERFORMANCE]
        if performance_issues:
            recommendations.append(
                "Review performance settings for production optimization"
            )
        
        # Maintainability recommendations
        if metrics.environment_variables_used < 10:
            recommendations.append(
                "Consider using more environment variables for better deployment flexibility"
            )
        
        if metrics.maintainability_score < 70:
            recommendations.append(
                "Improve configuration documentation and structure for better maintainability"
            )
        
        # Environment-specific recommendations
        environments = set()
        for file_data in review_results['files'].values():
            environments.add(file_data.get('environment', 'unknown'))
        
        if 'production' not in environments:
            recommendations.append(
                "Create a dedicated production configuration file"
            )
        
        if len(environments) < 3:
            recommendations.append(
                "Consider creating separate configurations for development, staging, and production"
            )
        
        return recommendations
    
    def _create_summary(self, review_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create review summary"""
        issues = review_results['issues']
        metrics = review_results['metrics']
        
        issue_counts = {
            'critical': len([i for i in issues if i.severity == SeverityLevel.CRITICAL]),
            'high': len([i for i in issues if i.severity == SeverityLevel.HIGH]),
            'medium': len([i for i in issues if i.severity == SeverityLevel.MEDIUM]),
            'low': len([i for i in issues if i.severity == SeverityLevel.LOW]),
            'info': len([i for i in issues if i.severity == SeverityLevel.INFO])
        }
        
        type_counts = {}
        for issue_type in ConfigurationIssueType:
            type_counts[issue_type.value.lower()] = len([i for i in issues if i.type == issue_type])
        
        # Determine overall health
        if issue_counts['critical'] > 0:
            overall_health = "CRITICAL"
        elif issue_counts['high'] > 3:
            overall_health = "POOR"
        elif issue_counts['high'] > 0 or issue_counts['medium'] > 5:
            overall_health = "FAIR"
        elif issue_counts['medium'] > 0:
            overall_health = "GOOD"
        else:
            overall_health = "EXCELLENT"
        
        return {
            'overall_health': overall_health,
            'total_issues': len(issues),
            'issue_counts': issue_counts,
            'type_counts': type_counts,
            'metrics': {
                'files_analyzed': metrics.total_files,
                'environments': metrics.total_environments,
                'sections': metrics.total_sections,
                'environment_variables': metrics.environment_variables_used,
                'maintainability_score': metrics.maintainability_score,
                'complexity_score': metrics.complexity_score
            }
        }
    
    def generate_report(self, review_results: Dict[str, Any], format: str = 'text') -> str:
        """Generate formatted report"""
        if format == 'json':
            return self._generate_json_report(review_results)
        else:
            return self._generate_text_report(review_results)
    
    def _generate_text_report(self, review_results: Dict[str, Any]) -> str:
        """Generate text-based report"""
        summary = review_results['summary']
        issues = review_results['issues']
        recommendations = review_results['recommendations']
        
        report = []
        report.append("=" * 70)
        report.append("YAML CONFIGURATION COMPREHENSIVE REVIEW REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Summary section
        report.append("📊 SUMMARY")
        report.append("-" * 20)
        report.append(f"Overall Health: {summary['overall_health']}")
        report.append(f"Total Issues: {summary['total_issues']}")
        report.append(f"Files Analyzed: {summary['metrics']['files_analyzed']}")
        report.append(f"Environments: {summary['metrics']['environments']}")
        report.append(f"Maintainability Score: {summary['metrics']['maintainability_score']:.1f}/100")
        report.append("")
        
        # Issue breakdown
        report.append("🔍 ISSUE BREAKDOWN")
        report.append("-" * 25)
        for severity, count in summary['issue_counts'].items():
            if count > 0:
                report.append(f"{severity.capitalize()}: {count}")
        report.append("")
        
        for issue_type, count in summary['type_counts'].items():
            if count > 0:
                report.append(f"{issue_type.capitalize()}: {count}")
        report.append("")
        
        # Critical and High issues
        critical_high_issues = [i for i in issues 
                              if i.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
        
        if critical_high_issues:
            report.append("🚨 CRITICAL & HIGH PRIORITY ISSUES")
            report.append("-" * 40)
            for issue in critical_high_issues:
                report.append(f"[{issue.severity.value}] {issue.title}")
                report.append(f"  📍 Location: {issue.location}")
                report.append(f"  📝 Description: {issue.description}")
                if issue.fix_suggestion:
                    report.append(f"  🔧 Fix: {issue.fix_suggestion}")
                report.append("")
        
        # Recommendations
        if recommendations:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 25)
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # File-by-file breakdown
        report.append("📁 FILE ANALYSIS")
        report.append("-" * 20)
        for filename, file_data in review_results['files'].items():
            file_issues = [i for i in issues if filename in i.location]
            report.append(f"{filename}: {len(file_issues)} issues ({file_data.get('environment', 'unknown')} env)")
        
        return "\n".join(report)
    
    def _generate_json_report(self, review_results: Dict[str, Any]) -> str:
        """Generate JSON report"""
        # Convert dataclasses to dictionaries for JSON serialization
        json_results = {
            'summary': review_results['summary'],
            'files': review_results['files'],
            'recommendations': review_results['recommendations'],
            'issues': []
        }
        
        for issue in review_results['issues']:
            json_results['issues'].append({
                'type': issue.type.value,
                'severity': issue.severity.value,
                'title': issue.title,
                'description': issue.description,
                'location': issue.location,
                'current_value': issue.current_value,
                'recommended_value': issue.recommended_value,
                'fix_suggestion': issue.fix_suggestion
            })
        
        return json.dumps(json_results, indent=2, ensure_ascii=False)


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YAML Configuration Comprehensive Review Tool")
    parser.add_argument('path', help='Path to configuration file or directory')
    parser.add_argument('--format', choices=['text', 'json'], default='text', 
                       help='Output format (default: text)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        reviewer = YAMLConfigurationReviewer()
        
        # Determine if path is file or directory
        path_obj = Path(args.path)
        
        if path_obj.is_file():
            # Review single file
            result = reviewer.review_configuration_file(str(path_obj))
            review_results = {
                'summary': {'overall_health': 'UNKNOWN', 'total_issues': len(result['issues'])},
                'files': {path_obj.name: result},
                'issues': result['issues'],
                'recommendations': []
            }
        elif path_obj.is_dir():
            # Review entire directory
            review_results = reviewer.review_configuration_system(str(path_obj))
        else:
            print(f"Error: Path '{args.path}' does not exist")
            return 1
        
        # Generate report
        report = reviewer.generate_report(review_results, args.format)
        
        # Output report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report written to {args.output}")
        else:
            print(report)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())