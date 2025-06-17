#!/usr/bin/env python3
"""
YAML Configuration Test Suite
============================

Comprehensive test suite for YAML configuration systems.
Includes unit tests, integration tests, and validation tests.

Author: Assistant  
Python Version: 3.8+
"""

import unittest
import io
import tempfile
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING
from dataclasses import dataclass
import logging

if TYPE_CHECKING:
    from yaml_config_review import (
        YAMLConfigurationReviewer,
        SecurityAnalyzer,
        PerformanceAnalyzer,
        MaintainabilityAnalyzer,
        EnvironmentAnalyzer,
        ConfigurationIssue,
        SeverityLevel,
        ConfigurationIssueType,
    )

try:
    from yaml_config_review import (
        YAMLConfigurationReviewer,
        SecurityAnalyzer,
        PerformanceAnalyzer,
        MaintainabilityAnalyzer,
        EnvironmentAnalyzer,
        ConfigurationIssue,
        SeverityLevel,
        ConfigurationIssueType,
    )
except ImportError:  # pragma: no cover - stubs for runtime
    from typing import Any

    YAMLConfigurationReviewer = Any
    SecurityAnalyzer = Any
    PerformanceAnalyzer = Any
    MaintainabilityAnalyzer = Any
    EnvironmentAnalyzer = Any
    ConfigurationIssue = Any
    SeverityLevel = Any
    ConfigurationIssueType = Any


class ConfigurationTestCase(unittest.TestCase):
    """Base test case for configuration testing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.reviewer = YAMLConfigurationReviewer()
        
        # Sample configurations for testing
        self.sample_configs = {
            'development': {
                'app': {
                    'debug': True,
                    'host': '127.0.0.1',
                    'port': 8050,
                    'title': 'Test App - Development'
                },
                'database': {
                    'type': 'mock',
                    'host': 'localhost',
                    'port': 5432
                },
                'security': {
                    'secret_key': 'dev-key-change-in-production',
                    'cors_enabled': False
                }
            },
            'production': {
                'app': {
                    'debug': False,
                    'host': '0.0.0.0',
                    'port': '${PORT:8050}',
                    'title': 'Test App - Production'
                },
                'database': {
                    'type': 'postgresql',
                    'host': '${DB_HOST}',
                    'port': '${DB_PORT:5432}',
                    'username': '${DB_USER}',
                    'password': '${DB_PASSWORD}'
                },
                'security': {
                    'secret_key': '${SECRET_KEY}',
                    'cors_enabled': True,
                    'cors_origins': ['${FRONTEND_URL}']
                }
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_config_file(self, filename: str, content: Dict[str, Any]) -> Path:
        """Create a configuration file for testing"""
        file_path = self.config_dir / filename
        with open(file_path, 'w') as f:
            yaml.dump(content, f, default_flow_style=False)
        return file_path
    
    def create_invalid_yaml_file(self, filename: str) -> Path:
        """Create an invalid YAML file for testing"""
        file_path = self.config_dir / filename
        with open(file_path, 'w') as f:
            f.write("invalid: yaml: content:\n  - missing\n    proper: indentation")
        return file_path


class TestSecurityAnalyzer(ConfigurationTestCase):
    """Test security analysis functionality"""
    
    def setUp(self):
        super().setUp()
        self.analyzer = SecurityAnalyzer()
    
    def test_hardcoded_secret_detection(self):
        """Test detection of hardcoded secrets"""
        config = {
            'security': {
                'secret_key': 'hardcoded-secret-key',
                'api_token': 'sk_live_123456789'
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect hardcoded secrets
        secret_issues = [i for i in issues if 'Hardcoded Secret' in i.title]
        self.assertGreater(len(secret_issues), 0)
        
        # Should suggest environment variables
        for issue in secret_issues:
            self.assertIn('${', str(issue.recommended_value))
    
    def test_insecure_default_detection(self):
        """Test detection of insecure default values"""
        config = {
            'security': {
                'secret_key': 'dev-key-change-in-production',
                'password': 'password'
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect insecure defaults
        default_issues = [i for i in issues if 'Insecure Default' in i.title]
        self.assertGreater(len(default_issues), 0)
        
        # Should be critical severity
        for issue in default_issues:
            self.assertEqual(issue.severity, SeverityLevel.CRITICAL)
    
    def test_production_security_checks(self):
        """Test production-specific security checks"""
        config = {
            'app': {
                'debug': True,
                'host': '127.0.0.1'
            }
        }
        
        context = {'file_path': 'production.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect debug mode in production
        debug_issues = [i for i in issues if 'Debug Mode' in i.title]
        self.assertGreater(len(debug_issues), 0)
        
        # Should detect localhost binding
        host_issues = [i for i in issues if 'Localhost Binding' in i.title]
        self.assertGreater(len(host_issues), 0)
    
    def test_cors_security_validation(self):
        """Test CORS configuration security validation"""
        config = {
            'security': {
                'cors_enabled': True,
                'cors_origins': ['*', 'https://example.com']
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect wildcard CORS
        cors_issues = [i for i in issues if 'Wildcard CORS' in i.title]
        self.assertGreater(len(cors_issues), 0)


class TestPerformanceAnalyzer(ConfigurationTestCase):
    """Test performance analysis functionality"""
    
    def setUp(self):
        super().setUp()
        self.analyzer = PerformanceAnalyzer()
    
    def test_database_performance_checks(self):
        """Test database performance configuration checks"""
        config = {
            'database': {
                'pool_size': 2,
                'connection_timeout': 120
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect small pool size
        pool_issues = [i for i in issues if 'Pool Size' in i.title]
        self.assertGreater(len(pool_issues), 0)
        
        # Should detect long timeout
        timeout_issues = [i for i in issues if 'Timeout' in i.title]
        self.assertGreater(len(timeout_issues), 0)
    
    def test_cache_performance_checks(self):
        """Test cache performance configuration checks"""
        config = {
            'cache': {
                'type': 'memory',
                'timeout_seconds': 30,
                'max_memory_mb': 25
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect short cache timeout
        timeout_issues = [i for i in issues if 'Cache Timeout' in i.title]
        self.assertGreater(len(timeout_issues), 0)
        
        # Should detect low memory limit
        memory_issues = [i for i in issues if 'Memory Cache' in i.title]
        self.assertGreater(len(memory_issues), 0)
    
    def test_analytics_performance_checks(self):
        """Test analytics performance configuration checks"""
        config = {
            'analytics': {
                'max_records_per_query': 150000,
                'batch_size': 15000
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect high record limit
        record_issues = [i for i in issues if 'Record Limit' in i.title]
        self.assertGreater(len(record_issues), 0)
        
        # Should detect large batch size
        batch_issues = [i for i in issues if 'Batch Size' in i.title]
        self.assertGreater(len(batch_issues), 0)


class TestMaintainabilityAnalyzer(ConfigurationTestCase):
    """Test maintainability analysis functionality"""
    
    def setUp(self):
        super().setUp()
        self.analyzer = MaintainabilityAnalyzer()
    
    def test_environment_variable_validation(self):
        """Test environment variable usage validation"""
        config = {
            'app': {
                'port': '${PORT}',  # No default
                'host': '${HOST:0.0.0.0}'  # With default
            }
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect missing default for PORT
        default_issues = [i for i in issues if 'Without Default' in i.title]
        self.assertGreater(len(default_issues), 0)
        
        # Should suggest adding default values
        for issue in default_issues:
            self.assertIn('default_value', str(issue.recommended_value))
    
    def test_configuration_structure_validation(self):
        """Test configuration structure validation"""
        config = {
            'app': {'debug': True},
            'unknown_section': {'value': 'test'},
            # Missing standard sections like 'database', 'security'
        }
        
        context = {'file_path': 'test.yaml', 'environment': 'development'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect missing sections
        missing_issues = [i for i in issues if 'Missing' in i.title]
        self.assertGreater(len(missing_issues), 0)
        
        # Should detect unknown sections
        unknown_issues = [i for i in issues if 'Unknown' in i.title]
        self.assertGreater(len(unknown_issues), 0)
    
    def test_documentation_checks(self):
        """Test documentation checking"""
        config = {'app': {'debug': True}}
        
        context = {
            'file_path': 'test.yaml',
            'environment': 'development',
            'raw_content': 'app:\n  debug: true\n'  # No comments
        }
        
        issues = self.analyzer.analyze(config, context)
        
        # Should detect lack of documentation
        doc_issues = [i for i in issues if 'Documentation' in i.title]
        self.assertGreater(len(doc_issues), 0)


class TestEnvironmentAnalyzer(ConfigurationTestCase):
    """Test environment-specific analysis functionality"""
    
    def setUp(self):
        super().setUp()
        self.analyzer = EnvironmentAnalyzer()
    
    def test_production_environment_checks(self):
        """Test production environment-specific checks"""
        config = {
            'app': {
                'enable_profiling': True,
                'log_level': 'DEBUG'
            },
            'monitoring': {
                'error_reporting_enabled': True
            }
        }
        
        context = {'file_path': 'production.yaml', 'environment': 'production'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect profiling in production
        profiling_issues = [i for i in issues if 'Profiling' in i.title]
        self.assertGreater(len(profiling_issues), 0)
        
        # Should detect debug logging in production
        logging_issues = [i for i in issues if 'Debug Logging' in i.title]
        self.assertGreater(len(logging_issues), 0)
    
    def test_development_environment_checks(self):
        """Test development environment-specific checks"""
        config = {
            'monitoring': {
                'error_reporting_enabled': True
            }
        }
        
        context = {'file_path': 'config.yaml', 'environment': 'development'}
        issues = self.analyzer.analyze(config, context)
        
        # Should suggest disabling error reporting in development
        error_reporting_issues = [i for i in issues if 'Error Reporting' in i.title]
        self.assertGreater(len(error_reporting_issues), 0)
    
    def test_environment_consistency_checks(self):
        """Test environment consistency validation"""
        config = {
            'app': {
                'title': 'My App'  # Doesn't indicate environment
            }
        }
        
        context = {'file_path': 'staging.yaml', 'environment': 'staging'}
        issues = self.analyzer.analyze(config, context)
        
        # Should detect missing environment in title
        title_issues = [i for i in issues if 'Environment Not in Title' in i.title]
        self.assertGreater(len(title_issues), 0)


class TestYAMLConfigurationReviewer(ConfigurationTestCase):
    """Test the main configuration reviewer"""
    
    def test_single_file_review(self):
        """Test reviewing a single configuration file"""
        config_file = self.create_config_file('test.yaml', self.sample_configs['development'])
        
        result = self.reviewer.review_configuration_file(str(config_file))
        
        self.assertTrue(result['valid'])
        self.assertIsInstance(result['issues'], list)
        self.assertEqual(result['environment'], 'development')
        self.assertIn('app', result['sections'])
    
    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML files"""
        invalid_file = self.create_invalid_yaml_file('invalid.yaml')
        
        result = self.reviewer.review_configuration_file(str(invalid_file))
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['issues']), 0)
        
        # Should have YAML parsing error
        parsing_errors = [i for i in result['issues'] if 'YAML Parsing' in i.title]
        self.assertGreater(len(parsing_errors), 0)
    
    def test_directory_review(self):
        """Test reviewing an entire configuration directory"""
        # Create multiple config files
        self.create_config_file('config.yaml', self.sample_configs['development'])
        self.create_config_file('production.yaml', self.sample_configs['production'])
        
        result = self.reviewer.review_configuration_system(str(self.config_dir))
        
        self.assertIn('summary', result)
        self.assertIn('files', result)
        self.assertIn('issues', result)
        self.assertIn('recommendations', result)
        
        # Should analyze both files
        self.assertEqual(len(result['files']), 2)
        
        # Should have metrics
        self.assertIn('metrics', result)
    
    def test_environment_detection(self):
        """Test environment detection from filenames"""
        test_cases = [
            ('production.yaml', 'production'),
            ('prod.yaml', 'production'),
            ('staging.yaml', 'staging'),
            ('test.yaml', 'test'),
            ('config.yaml', 'development'),
            ('random.yaml', 'unknown')
        ]
        
        for filename, expected_env in test_cases:
            detected_env = self.reviewer._determine_environment(filename)
            self.assertEqual(detected_env, expected_env, 
                           f"Failed for {filename}: expected {expected_env}, got {detected_env}")
    
    def test_report_generation(self):
        """Test report generation in different formats"""
        # Create sample review results
        self.create_config_file('config.yaml', self.sample_configs['development'])
        result = self.reviewer.review_configuration_system(str(self.config_dir))
        
        # Test text report
        text_report = self.reviewer.generate_report(result, 'text')
        self.assertIn('YAML CONFIGURATION', text_report)
        self.assertIn('SUMMARY', text_report)
        
        # Test JSON report
        json_report = self.reviewer.generate_report(result, 'json')
        parsed_json = json.loads(json_report)
        self.assertIn('summary', parsed_json)
        self.assertIn('issues', parsed_json)


class TestConfigurationValidation(ConfigurationTestCase):
    """Test configuration validation utilities"""
    
    def test_environment_variable_counting(self):
        """Test counting of environment variables"""
        config = {
            'app': {
                'port': '${PORT:8050}',
                'host': '${HOST}',
                'title': 'App'
            },
            'database': {
                'url': '${DB_URL}',
                'password': '${DB_PASS:default}'
            }
        }
        
        count = self.reviewer._count_environment_variables(config)
        self.assertEqual(count, 4)  # PORT, HOST, DB_URL, DB_PASS
    
    def test_metrics_calculation(self):
        """Test metrics calculation"""
        # Create multiple config files
        self.create_config_file('dev.yaml', self.sample_configs['development'])
        self.create_config_file('prod.yaml', self.sample_configs['production'])
        
        result = self.reviewer.review_configuration_system(str(self.config_dir))
        metrics = result['metrics']
        
        self.assertEqual(metrics.total_files, 2)
        self.assertGreater(metrics.total_environments, 0)
        self.assertGreater(metrics.total_sections, 0)
        self.assertGreaterEqual(metrics.maintainability_score, 0)
        self.assertLessEqual(metrics.maintainability_score, 100)


class TestIntegration(ConfigurationTestCase):
    """Integration tests for the complete system"""
    
    def test_comprehensive_analysis_workflow(self):
        """Test complete analysis workflow"""
        # Create a comprehensive configuration set
        configs = {
            'config.yaml': self.sample_configs['development'],
            'production.yaml': self.sample_configs['production'],
            'staging.yaml': {
                'app': {
                    'debug': False,
                    'host': '0.0.0.0',
                    'port': '${PORT:8050}',
                    'title': 'Test App - Staging'
                },
                'database': {
                    'type': 'postgresql',
                    'host': '${DB_HOST:staging-db}',
                    'pool_size': 8
                }
            }
        }
        
        for filename, config in configs.items():
            self.create_config_file(filename, config)
        
        # Run complete analysis
        result = self.reviewer.review_configuration_system(str(self.config_dir))
        
        # Verify comprehensive results
        self.assertEqual(len(result['files']), 3)
        self.assertIn('summary', result)
        self.assertIn('recommendations', result)
        
        # Should detect various issues
        security_issues = [i for i in result['issues'] 
                          if i.type == ConfigurationIssueType.SECURITY]
        self.assertGreater(len(security_issues), 0)
        
        # Should have recommendations
        self.assertGreater(len(result['recommendations']), 0)
        
        # Test report generation
        text_report = self.reviewer.generate_report(result, 'text')
        self.assertIn('COMPREHENSIVE REVIEW', text_report)
        
        json_report = self.reviewer.generate_report(result, 'json')
        parsed = json.loads(json_report)
        self.assertIn('summary', parsed)


class ConfigurationTestRunner:
    """Test runner with detailed reporting"""
    
    def __init__(self):
        self.test_suites = [
            TestSecurityAnalyzer,
            TestPerformanceAnalyzer,
            TestMaintainabilityAnalyzer,
            TestEnvironmentAnalyzer,
            TestYAMLConfigurationReviewer,
            TestConfigurationValidation,
            TestIntegration
        ]
    
    def run_all_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run all test suites and return results"""
        results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'suite_results': {},
            'failures': [],
            'errors': []
        }
        
        for suite_class in self.test_suites:
            suite_result = self.run_test_suite(suite_class, verbose)
            
            suite_name = suite_class.__name__
            results['suite_results'][suite_name] = suite_result
            
            results['total_tests'] += suite_result['tests_run']
            results['passed'] += suite_result['tests_run'] - len(suite_result['failures']) - len(suite_result['errors'])
            results['failed'] += len(suite_result['failures'])
            results['errors'] += len(suite_result['errors'])
            
            results['failures'].extend(suite_result['failures'])
            results['errors'].extend(suite_result['errors'])
        
        return results
    
    def run_test_suite(self, suite_class, verbose: bool = False) -> Dict[str, Any]:
        """Run a single test suite"""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(suite_class)
        
        # Capture test results
        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2 if verbose else 1)
        result = runner.run(suite)
        
        return {
            'tests_run': result.testsRun,
            'failures': [str(failure) for failure in result.failures],
            'errors': [str(error) for error in result.errors],
            'skipped': [str(skip) for skip in result.skipped],
            'success': result.wasSuccessful(),
            'output': stream.getvalue()
        }
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 70)
        report.append("YAML CONFIGURATION TEST SUITE REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Summary
        report.append("📊 TEST SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Tests: {results['total_tests']}")
        report.append(f"Passed: {results['passed']}")
        report.append(f"Failed: {results['failed']}")
        report.append(f"Errors: {results['errors']}")
        report.append(f"Success Rate: {(results['passed'] / max(results['total_tests'], 1)) * 100:.1f}%")
        report.append("")
        
        # Suite breakdown
        report.append("📁 SUITE BREAKDOWN")
        report.append("-" * 25)
        for suite_name, suite_result in results['suite_results'].items():
            status = "✅ PASS" if suite_result['success'] else "❌ FAIL"
            report.append(f"{suite_name}: {status} ({suite_result['tests_run']} tests)")
        report.append("")
        
        # Failures and errors
        if results['failures'] or results['errors']:
            report.append("🚨 FAILURES AND ERRORS")
            report.append("-" * 30)
            
            for i, failure in enumerate(results['failures'], 1):
                report.append(f"FAILURE {i}:")
                report.append(failure)
                report.append("")
            
            for i, error in enumerate(results['errors'], 1):
                report.append(f"ERROR {i}:")
                report.append(error)
                report.append("")
        
        return "\n".join(report)


def main():
    """Main function for running tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YAML Configuration Test Suite")
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose test output')
    parser.add_argument('--suite', '-s', help='Run specific test suite')
    parser.add_argument('--output', '-o', help='Output report to file')
    
    args = parser.parse_args()
    
    runner = ConfigurationTestRunner()
    
    if args.suite:
        # Run specific suite
        suite_class = None
        for cls in runner.test_suites:
            if cls.__name__.lower() == args.suite.lower():
                suite_class = cls
                break
        
        if not suite_class:
            print(f"Unknown test suite: {args.suite}")
            print("Available suites:")
            for cls in runner.test_suites:
                print(f"  - {cls.__name__}")
            return 1
        
        result = runner.run_test_suite(suite_class, args.verbose)
        success = result['success']
        print(result['output'])
    else:
        # Run all tests
        results = runner.run_all_tests(args.verbose)
        report = runner.generate_test_report(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Test report written to {args.output}")
        else:
            print(report)
        
        success = results['failed'] == 0 and results['errors'] == 0
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())