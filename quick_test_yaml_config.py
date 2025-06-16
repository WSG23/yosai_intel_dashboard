# quick_test_yaml_config.py - FINAL: Complete YAML system verification
"""
Quick test script to verify your complete YAML configuration system
Run this to instantly verify everything is working correctly
"""

import os
import sys
import tempfile
from pathlib import Path

def test_yaml_imports():
    """Test if all YAML config components can be imported"""
    print("🔍 Testing YAML Configuration Imports...")
    
    try:
        from config.yaml_config import (
            ConfigurationManager, ConfigurationError,
            AppConfig, DatabaseConfig, SecurityConfig,
            get_configuration_manager
        )
        print("✅ YAML configuration classes imported")
        return True
    except ImportError as e:
        print(f"❌ YAML import failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration loading with defaults"""
    print("\n🔧 Testing Configuration Loading...")
    
    try:
        from config.yaml_config import ConfigurationManager
        
        config_manager = ConfigurationManager()
        config_manager.load_configuration()  # Should use defaults if no file
        
        # Check basic config structure
        assert config_manager.app_config.port == 8050
        assert config_manager.database_config.type == "mock"
        assert config_manager.security_config.max_file_size_mb == 100
        
        print("✅ Default configuration loaded successfully")
        print(f"   📂 App: {config_manager.app_config.host}:{config_manager.app_config.port}")
        print(f"   🗄️  Database: {config_manager.database_config.type}")
        print(f"   🔒 Max file size: {config_manager.security_config.max_file_size_mb}MB")
        
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_environment_variable_substitution():
    """Test environment variable substitution"""
    print("\n🌍 Testing Environment Variable Substitution...")
    
    try:
        from config.yaml_config import ConfigurationManager
        
        # Create a test config with environment variables
        test_config = """
app:
  port: ${TEST_PORT:8080}
  debug: ${TEST_DEBUG:true}
  title: ${TEST_TITLE:Test Dashboard}

database:
  type: ${DB_TYPE:mock}
  host: ${DB_HOST:localhost}
"""
        
        # Set some environment variables
        os.environ['TEST_PORT'] = '9999'
        os.environ['TEST_DEBUG'] = 'false'
        os.environ['DB_TYPE'] = 'postgresql'
        # DB_HOST not set - should use default
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(test_config)
            temp_config_path = f.name
        
        try:
            # Load configuration
            config_manager = ConfigurationManager()
            config_manager.load_configuration(temp_config_path)
            
            # Verify substitution worked
            assert config_manager.app_config.port == 9999
            assert config_manager.app_config.debug == False
            assert config_manager.app_config.title == "Test Dashboard"
            assert config_manager.database_config.type == "postgresql"
            assert config_manager.database_config.host == "localhost"
            
            print("✅ Environment variable substitution working")
            print(f"   🔢 Port: {config_manager.app_config.port} (from TEST_PORT)")
            print(f"   🐛 Debug: {config_manager.app_config.debug} (from TEST_DEBUG)")
            print(f"   🗄️  DB Type: {config_manager.database_config.type} (from DB_TYPE)")
            print(f"   🏠 DB Host: {config_manager.database_config.host} (default)")
            
            return True
            
        finally:
            # Clean up
            os.unlink(temp_config_path)
            for var in ['TEST_PORT', 'TEST_DEBUG', 'DB_TYPE']:
                os.environ.pop(var, None)
    
    except Exception as e:
        print(f"❌ Environment substitution failed: {e}")
        return False

def test_configuration_validation():
    """Test configuration validation"""
    print("\n✅ Testing Configuration Validation...")
    
    try:
        from config.yaml_config import ConfigurationManager, AppConfig, DatabaseConfig
        
        # Test valid configuration
        valid_app_config = AppConfig(port=8050, log_level="INFO")
        print("✅ Valid configuration accepted")
        
        # Test invalid configurations
        try:
            invalid_port = AppConfig(port=999999)
            print("❌ Should have rejected invalid port")
            return False
        except ValueError:
            print("✅ Invalid port rejected correctly")
        
        try:
            invalid_log_level = AppConfig(log_level="INVALID")
            print("❌ Should have rejected invalid log level")
            return False
        except ValueError:
            print("✅ Invalid log level rejected correctly")
        
        try:
            invalid_db_type = DatabaseConfig(type="invalid_database")
            print("❌ Should have rejected invalid database type")
            return False
        except ValueError:
            print("✅ Invalid database type rejected correctly")
        
        return True
    
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def test_di_integration():
    """Test DI container integration with YAML config"""
    print("\n🔧 Testing DI Container Integration...")
    
    try:
        from core.service_registry import get_configured_container_with_yaml
        from config.yaml_config import get_configuration_manager
        
        # Get configured container
        container = get_configured_container_with_yaml()
        
        # Test that config services are available
        config_manager = container.get('config_manager')
        app_config = container.get('app_config')
        database_config = container.get('database_config')
        
        assert config_manager is not None
        assert app_config is not None
        assert database_config is not None
        
        print("✅ DI container configured with YAML")
        print(f"   📋 Config manager: {type(config_manager).__name__}")
        print(f"   🏠 App config: {app_config.host}:{app_config.port}")
        print(f"   🗄️  Database config: {database_config.type}")
        
        # Test service creation with config
        database = container.get('database')
        cache_manager = container.get('cache_manager')
        
        assert database is not None
        assert cache_manager is not None
        
        print("✅ Services created with configuration")
        print(f"   🗄️  Database: {type(database).__name__}")
        print(f"   💾 Cache: {type(cache_manager).__name__}")
        
        return True
    
    except Exception as e:
        print(f"❌ DI integration failed: {e}")
        return False

def test_app_creation():
    """Test complete app creation with YAML config"""
    print("\n🚀 Testing App Creation...")
    
    try:
        from core.app_factory import create_application
        
        # Create app
        app = create_application()
        
        if app is None:
            print("❌ App creation returned None")
            return False
        
        # Test app has config methods
        assert hasattr(app, 'config_manager')
        assert hasattr(app, 'container')
        assert hasattr(app, 'get_service')
        assert hasattr(app, 'config_health')
        
        config_manager = app.config_manager
        container = app.container
        
        print("✅ App created with YAML configuration")
        print(f"   📋 Title: {config_manager.app_config.title}")
        print(f"   🌐 Host: {config_manager.app_config.host}:{config_manager.app_config.port}")
        print(f"   🔧 Debug: {config_manager.app_config.debug}")
        
        # Test service access through app
        analytics_service = app.get_service_optional('analytics_service')
        database = app.get_service_optional('database')
        
        print(f"   📊 Analytics service: {'✅' if analytics_service else '❌'}")
        print(f"   🗄️  Database service: {'✅' if database else '❌'}")
        
        return True
    
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_health_monitoring():
    """Test health monitoring with config"""
    print("\n🏥 Testing Health Monitoring...")
    
    try:
        from core.app_factory import create_application
        
        app = create_application()
        if app is None:
            print("❌ No app for health testing")
            return False
        
        # Test container health
        container_health = app.container_health()
        assert 'status' in container_health
        
        # Test config health
        config_health = app.config_health()
        assert 'warnings' in config_health
        assert 'environment' in config_health
        
        print("✅ Health monitoring working")
        print(f"   🏥 Container status: {container_health['status']}")
        print(f"   📋 Config warnings: {len(config_health['warnings'])}")
        print(f"   🌍 Environment: {config_health['environment']}")
        
        # Test service health monitor
        health_monitor = app.get_service_optional('health_monitor')
        if health_monitor:
            health_status = health_monitor.get_health_status()
            print(f"   🩺 System health: {health_status['overall']}")
            
            components = health_status.get('components', {})
            for component, status in components.items():
                print(f"   📦 {component}: {status.get('status', 'unknown')}")
        
        return True
    
    except Exception as e:
        print(f"❌ Health monitoring failed: {e}")
        return False

def test_production_readiness():
    """Test production readiness features"""
    print("\n🏭 Testing Production Readiness...")
    
    try:
        from config.yaml_config import ConfigurationManager
        
        # Test with production-like settings
        config_manager = ConfigurationManager()
        config_manager.load_configuration()
        
        # Set production-like config
        config_manager.app_config.debug = False
        config_manager.app_config.host = "0.0.0.0"
        config_manager.security_config.secret_key = "production-secret-key-very-secure"
        
        # Test validation warnings
        warnings = config_manager.validate_configuration()
        
        print("✅ Production validation working")
        print(f"   ⚠️  Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"      • {warning}")
        
        # Test effective configuration export
        effective_config = config_manager.get_effective_configuration()
        assert '_meta' in effective_config
        assert len(effective_config) >= 6  # All config sections
        
        print("✅ Configuration export working")
        print(f"   📦 Sections: {len(effective_config) - 1}")  # -1 for _meta
        
        return True
    
    except Exception as e:
        print(f"❌ Production readiness test failed: {e}")
        return False

def main():
    """Run complete YAML configuration system test"""
    print("🏯 YŌSAI INTEL - YAML CONFIGURATION SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("YAML Imports", test_yaml_imports),
        ("Configuration Loading", test_configuration_loading),
        ("Environment Variables", test_environment_variable_substitution),
        ("Config Validation", test_configuration_validation),
        ("DI Integration", test_di_integration),
        ("App Creation", test_app_creation),
        ("Health Monitoring", test_health_monitoring),
        ("Production Readiness", test_production_readiness)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   💥 {test_name} had issues!")
        except Exception as e:
            print(f"   💥 {test_name} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Your YAML Configuration System is COMPLETE and READY!")
        print("\n🚀 Production Features Available:")
        print("   ✓ Environment variable substitution")
        print("   ✓ Environment-specific configs")
        print("   ✓ Configuration validation")
        print("   ✓ DI container integration")
        print("   ✓ Health monitoring")
        print("   ✓ Production readiness checks")
        
        print("\n📋 Usage Examples:")
        print("   Development:  python app.py")
        print("   Production:   YOSAI_ENV=production python app.py")
        print("   Custom:       YOSAI_CONFIG_FILE=my_config.yaml python app.py")
        print("   Validation:   python validate_config.py")
        
    else:
        print("⚠️  Some tests failed")
        print("\n🔧 Common fixes:")
        print("   • Install PyYAML: pip install PyYAML")
        print("   • Check config/ directory exists")
        print("   • Verify core/ directory has DI files")
        print("   • Run from project root directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 YAML Configuration System Status: COMPLETE! ⭐⭐⭐")
        print("Ready for production deployment!")
    else:
        print("\n❌ System needs attention before production use")
    
    sys.exit(0 if success else 1)