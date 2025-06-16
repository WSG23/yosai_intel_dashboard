# verify_yaml_config.py - Complete YAML Configuration System Verification
"""
Complete verification script for the YAML configuration system
Run this to verify Priority 3: Configuration Management is working correctly
"""

import sys
import os
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple

def test_basic_imports() -> Tuple[bool, str]:
    """Test that all configuration modules can be imported"""
    try:
        from config.yaml_config import (
            ConfigurationManager,
            EnvironmentOverrideProcessor,
            ConfigurationValidator,
            AppConfig,
            DatabaseConfig,
            CacheConfig,
            SecurityConfig
        )
        from core.service_registry import configure_container_with_yaml
        from core.app_factory import create_application
        from core.container import Container
        
        return True, "All imports successful"
    except ImportError as e:
        return False, f"Import failed: {e}"
    except Exception as e:
        return False, f"Import error: {e}"

def test_default_configuration() -> Tuple[bool, str]:
    """Test loading default configuration"""
    try:
        from config.yaml_config import ConfigurationManager
        
        config_manager = ConfigurationManager()
        config_manager.load_configuration(None)
        
        # Verify basic configuration
        if config_manager.app_config.host != '127.0.0.1':
            return False, "Default host not set correctly"
        
        if config_manager.app_config.port != 8050:
            return False, "Default port not set correctly"
        
        if config_manager.database_config.type != 'mock':
            return False, "Default database type not set correctly"
        
        return True, "Default configuration loaded successfully"
        
    except Exception as e:
        return False, f"Default configuration failed: {e}"

def test_yaml_file_loading() -> Tuple[bool, str]:
    """Test loading configuration from YAML file"""
    try:
        from config.yaml_config import ConfigurationManager
        
        # Create test YAML config
        test_config = {
            'app': {
                'debug': False,
                'host': '0.0.0.0',
                'port': 9000,
                'title': 'Test Dashboard'
            },
            'database': {
                'type': 'postgresql',
                'host': 'test-db',
                'port': 5433
            },
            'cache': {
                'type': 'redis',
                'timeout_seconds': 600
            }
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            # Load configuration
            config_manager = ConfigurationManager()
            config_manager.load_configuration(temp_file)
            
            # Verify loaded values
            if config_manager.app_config.debug != False:
                return False, "YAML debug value not loaded correctly"
            
            if config_manager.app_config.host != '0.0.0.0':
                return False, "YAML host value not loaded correctly"
            
            if config_manager.app_config.port != 9000:
                return False, "YAML port value not loaded correctly"
            
            if config_manager.database_config.type != 'postgresql':
                return False, "YAML database type not loaded correctly"
            
            if config_manager.cache_config.type != 'redis':
                return False, "YAML cache type not loaded correctly"
            
            return True, "YAML file loading works correctly"
            
        finally:
            # Clean up
            os.unlink(temp_file)
        
    except Exception as e:
        return False, f"YAML file loading failed: {e}"

def test_environment_overrides() -> Tuple[bool, str]:
    """Test environment variable overrides"""
    try:
        from config.yaml_config import EnvironmentOverrideProcessor
        
        # Store original environment
        original_env = dict(os.environ)
        
        try:
            # Set test environment variables
            os.environ['DB_HOST'] = 'override-host'
            os.environ['DB_PORT'] = '9999'
            os.environ['DEBUG'] = 'false'
            os.environ['YOSAI_APP_TITLE'] = 'Override Title'
            
            # Create test config
            config = {
                'app': {'debug': True, 'title': 'Original Title'},
                'database': {'host': 'localhost', 'port': 5432}
            }
            
            # Process overrides
            processor = EnvironmentOverrideProcessor()
            result = processor.process_overrides(config)
            
            # Verify overrides
            if result['database']['host'] != 'override-host':
                return False, "DB_HOST override failed"
            
            if result['database']['port'] != 9999:
                return False, "DB_PORT override failed"
            
            if result['app']['debug'] != False:
                return False, "DEBUG override failed"
            
            if result['app']['title'] != 'Override Title':
                return False, "YOSAI_APP_TITLE override failed"
            
            return True, "Environment overrides work correctly"
            
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
        
    except Exception as e:
        return False, f"Environment override test failed: {e}"

def test_configuration_validation() -> Tuple[bool, str]:
    """Test configuration validation"""
    try:
        from config.yaml_config import ConfigurationValidator
        
        # Test configuration with issues
        problem_config = {
            'app': {'debug': True, 'host': '0.0.0.0'},
            'security': {'secret_key': 'dev-key-change-in-production'},
            'database': {'type': 'postgresql', 'password': ''},
            'monitoring': {'error_reporting_enabled': True, 'sentry_dsn': None}
        }
        
        warnings = ConfigurationValidator.validate(problem_config)
        
        # Should detect multiple issues
        if len(warnings) < 3:
            return False, f"Expected multiple warnings, got {len(warnings)}"
        
        # Check for specific warnings
        warning_text = ' '.join(warnings).lower()
        
        if 'debug' not in warning_text:
            return False, "Debug mode warning not detected"
        
        if 'secret' not in warning_text:
            return False, "Secret key warning not detected"
        
        if 'password' not in warning_text:
            return False, "Password warning not detected"
        
        return True, f"Configuration validation detected {len(warnings)} issues correctly"
        
    except Exception as e:
        return False, f"Configuration validation test failed: {e}"

def test_dependency_injection_integration() -> Tuple[bool, str]:
    """Test integration with dependency injection container"""
    try:
        from config.yaml_config import ConfigurationManager
        from core.service_registry import configure_container_with_yaml
        from core.container import Container
        
        # Create configuration
        config_manager = ConfigurationManager()
        config_manager.load_configuration(None)
        
        # Create container and configure it
        container = Container()
        configure_container_with_yaml(container, config_manager)
        
        # Verify configuration objects are registered
        required_services = [
            'config_manager', 'app_config', 'database_config', 
            'cache_config', 'security_config'
        ]
        
        for service in required_services:
            if not container.has(service):
                return False, f"Service '{service}' not registered in container"
        
        # Verify services can be retrieved
        app_config = container.get('app_config')
        if app_config.host != '127.0.0.1':
            return False, "Retrieved app_config has incorrect values"
        
        database = container.get('database')
        if database is None:
            return False, "Database service not created"
        
        cache_manager = container.get('cache_manager')
        if cache_manager is None:
            return False, "Cache manager service not created"
        
        return True, "DI integration works correctly"
        
    except Exception as e:
        return False, f"DI integration test failed: {e}"

def test_app_creation() -> Tuple[bool, str]:
    """Test creating application with YAML configuration"""
    try:
        from core.app_factory import create_application_for_testing
        
        # Create test application
        app = create_application_for_testing()
        
        if app is None:
            return False, "Failed to create test application"
        
        # Verify app has configuration access methods
        if not hasattr(app, 'get_service'):
            return False, "App missing get_service method"
        
        if not hasattr(app, 'get_config'):
            return False, "App missing get_config method"
        
        # Test service access
        config_manager = app.get_config()
        if config_manager is None:
            return False, "Failed to get config manager from app"
        
        # Test container health
        health = app.container_health()
        if 'status' not in health:
            return False, "Container health check failed"
        
        return True, "Application creation with YAML config works"
        
    except Exception as e:
        return False, f"App creation test failed: {e}"

def test_existing_config_files() -> Tuple[bool, str]:
    """Test that existing config files can be loaded"""
    try:
        from config.yaml_config import ConfigurationManager
        
        config_files = [
            'config/config.yaml',
            'config/production.yaml', 
            'config/test.yaml'
        ]
        
        loaded_files = []
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    config_manager = ConfigurationManager()
                    config_manager.load_configuration(config_file)
                    loaded_files.append(config_file)
                except Exception as e:
                    return False, f"Failed to load {config_file}: {e}"
        
        if not loaded_files:
            return False, "No existing config files found to test"
        
        return True, f"Successfully loaded existing config files: {', '.join(loaded_files)}"
        
    except Exception as e:
        return False, f"Existing config file test failed: {e}"

def run_all_tests() -> List[Tuple[str, bool, str]]:
    """Run all verification tests"""
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Default Configuration", test_default_configuration),
        ("YAML File Loading", test_yaml_file_loading),
        ("Environment Overrides", test_environment_overrides),
        ("Configuration Validation", test_configuration_validation),
        ("DI Integration", test_dependency_injection_integration),
        ("App Creation", test_app_creation),
        ("Existing Config Files", test_existing_config_files),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Testing {test_name}...")
        try:
            success, message = test_func()
            results.append((test_name, success, message))
            
            if success:
                print(f"   ✅ {message}")
            else:
                print(f"   ❌ {message}")
        except Exception as e:
            results.append((test_name, False, f"Test crashed: {e}"))
            print(f"   💥 Test crashed: {e}")
    
    return results

def print_summary(results: List[Tuple[str, bool, str]]) -> None:
    """Print test summary"""
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    
    print("\n" + "=" * 70)
    print("📊 YAML CONFIGURATION SYSTEM - VERIFICATION RESULTS")
    print("=" * 70)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your YAML configuration system is working perfectly!")
        
        print(f"\n✅ Verified Features:")
        print(f"   • YAML file loading and parsing")
        print(f"   • Environment variable overrides") 
        print(f"   • Configuration validation and warnings")
        print(f"   • Type-safe configuration objects")
        print(f"   • Dependency injection integration")
        print(f"   • Multi-environment support")
        print(f"   • Application factory integration")
        
        print(f"\n🚀 Ready for Production!")
        print(f"   • All configuration features working")
        print(f"   • Environment overrides functional")
        print(f"   • DI container integration complete")
        print(f"   • Health monitoring enabled")
        
        print(f"\n📋 Quick Usage Examples:")
        print(f"   python app.py                              # Default config")
        print(f"   YOSAI_ENV=production python app.py         # Production config")
        print(f"   DB_HOST=mydb DEBUG=false python app.py     # Environment overrides")
        
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Issues found:")
        
        for test_name, success, message in results:
            if not success:
                print(f"   ❌ {test_name}: {message}")
        
        print(f"\n🔧 Troubleshooting Steps:")
        print(f"   1. Check that all required files exist:")
        print(f"      - config/yaml_config.py")
        print(f"      - config/config.yaml") 
        print(f"      - core/service_registry.py")
        print(f"      - core/app_factory.py")
        print(f"   2. Install required dependencies:")
        print(f"      pip install pyyaml")
        print(f"   3. Check for syntax errors in config files")
        print(f"   4. Verify directory structure")

def main() -> None:
    """Main verification function"""
    print("🏯 YŌSAI INTEL DASHBOARD")
    print("🔧 Priority 3: Configuration Management Verification")
    print("=" * 70)
    print("Testing YAML configuration system with environment overrides...")
    print()
    
    # Run all verification tests
    results = run_all_tests()
    
    # Print summary
    print_summary(results)
    
    # Return appropriate exit code
    all_passed = all(success for _, success, _ in results)
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
    