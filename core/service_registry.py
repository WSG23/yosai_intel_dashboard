# core/service_registry.py - UPDATED: DI integration with YAML configuration
"""
Enhanced service registry with YAML configuration integration
"""
from typing import Any
import logging
from .container import Container, get_container
from config.yaml_config import ConfigurationManager, get_configuration_manager

logger = logging.getLogger(__name__)

def configure_container_with_yaml(container: Container) -> None:
    """Configure the container with YAML configuration support"""
    
    # 1. CONFIGURATION (Foundation) - Now uses YAML
    container.register(
        'config_manager',
        get_configuration_manager,
        singleton=True
    )
    
    # Register individual config sections for easy access
    container.register(
        'app_config',
        lambda config_manager: config_manager.app_config,
        singleton=True,
        dependencies=['config_manager']
    )
    
    container.register(
        'database_config',
        lambda config_manager: config_manager.database_config,
        singleton=True,
        dependencies=['config_manager']
    )
    
    container.register(
        'analytics_config',
        lambda config_manager: config_manager.analytics_config,
        singleton=True,
        dependencies=['config_manager']
    )
    
    container.register(
        'security_config',
        lambda config_manager: config_manager.security_config,
        singleton=True,
        dependencies=['config_manager']
    )
    
    # 2. DATABASE (Depends on database_config)
    container.register(
        'database',
        create_database_with_yaml_config,
        singleton=True,
        dependencies=['database_config']
    )
    
    # 3. CACHE (Depends on cache_config)
    container.register(
        'cache_manager',
        create_cache_with_yaml_config,
        singleton=True,
        dependencies=['config_manager']
    )
    
    # 4. MODELS (Depend on database)
    container.register(
        'access_model',
        create_access_model,
        singleton=True,
        dependencies=['database']
    )
    
    container.register(
        'anomaly_model', 
        create_anomaly_model,
        singleton=True,
        dependencies=['database']
    )
    
    # 5. SERVICES (Depend on models and config)
    container.register(
        'analytics_service',
        create_analytics_service_with_config,
        singleton=True,
        dependencies=['access_model', 'anomaly_model', 'analytics_config', 'cache_manager']
    )
    
    container.register(
        'file_processor',
        create_file_processor_with_config,
        singleton=True,
        dependencies=['security_config']
    )
    
    # 6. MONITORING SERVICES
    container.register(
        'health_monitor',
        create_health_monitor,
        singleton=True,
        dependencies=['config_manager', 'database', 'cache_manager']
    )
    
    logger.info("Container configured with YAML configuration system")

def create_database_with_yaml_config(database_config) -> Any:
    """Create database connection using YAML configuration"""
    try:
        from config.database_manager import DatabaseManager, DatabaseConfig
        
        # Convert YAML config to DatabaseConfig
        db_config = DatabaseConfig(
            db_type=database_config.type,
            host=database_config.host,
            port=database_config.port,
            database=database_config.database,
            username=database_config.username,
            password=database_config.password,
            pool_size=database_config.pool_size
        )
        
        return DatabaseManager.create_connection(db_config)
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        # Return mock database as fallback
        from config.database_manager import MockDatabaseConnection
        return MockDatabaseConnection()

def create_cache_with_yaml_config(config_manager: ConfigurationManager) -> Any:
    """Create cache manager using YAML configuration"""
    cache_config = config_manager.cache_config
    
    if cache_config.type == "redis":
        return RedisaCacheManager(cache_config)
    elif cache_config.type == "memory":
        return MemoryCacheManager(cache_config)
    else:
        return NullCacheManager()

def create_analytics_service_with_config(access_model: Any, anomaly_model: Any, 
                                       analytics_config: Any, cache_manager: Any) -> Any:
    """Create analytics service with YAML configuration"""
    try:
        from services.analytics_service import AnalyticsService, AnalyticsConfig
        
        # Convert YAML config to AnalyticsConfig
        service_config = AnalyticsConfig(
            default_time_range_days=30,
            max_records_per_query=analytics_config.max_records_per_query,
            cache_timeout_seconds=analytics_config.cache_timeout_seconds,
            min_confidence_threshold=0.7
        )
        
        return AnalyticsService(service_config)
        
    except Exception as e:
        logger.error(f"Failed to create analytics service: {e}")
        return None

def create_file_processor_with_config(security_config: Any) -> Any:
    """Create file processor with security configuration"""
    try:
        from components.analytics.file_processing import FileProcessor
        
        # Use security config for file validation
        FileProcessor.MAX_FILE_SIZE = security_config.max_file_size_mb * 1024 * 1024
        FileProcessor.ALLOWED_EXTENSIONS = set(
            ext.lstrip('.') for ext in security_config.allowed_file_types
        )
        
        return FileProcessor()
    except Exception as e:
        logger.error(f"Failed to create file processor: {e}")
        return None

def create_health_monitor(config_manager: ConfigurationManager, 
                         database: Any, cache_manager: Any) -> Any:
    """Create health monitor with full system monitoring"""
    return EnhancedHealthMonitor(config_manager, database, cache_manager)

def create_access_model(database: Any) -> Any:
    """Create access model using existing factory"""
    try:
        from models.access_events import create_access_event_model
        return create_access_event_model(database)
    except Exception as e:
        logger.error(f"Failed to create access model: {e}")
        return None

def create_anomaly_model(database: Any) -> Any:
    """Create anomaly model using existing factory"""
    try:
        from models.base import ModelFactory
        return ModelFactory.create_anomaly_model(database)
    except Exception as e:
        logger.error(f"Failed to create anomaly model: {e}")
        return None

# Enhanced cache managers with YAML config support
class MemoryCacheManager:
    """Memory-based cache manager with YAML config"""
    
    def __init__(self, cache_config):
        self.config = cache_config
        self._cache = {}
        self.max_size = cache_config.max_memory_mb * 1024 * 1024 if cache_config.max_memory_mb else None
        self.key_prefix = cache_config.key_prefix
    
    def get(self, key: str) -> Any:
        """Get from cache with key prefix"""
        full_key = f"{self.key_prefix}{key}"
        return self._cache.get(full_key)
    
    def set(self, key: str, value: Any) -> None:
        """Set cache value with key prefix"""
        full_key = f"{self.key_prefix}{key}"
        
        # Simple size management
        if self.max_size and len(self._cache) > 1000:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._cache.keys())[:100]
            for k in keys_to_remove:
                del self._cache[k]
        
        self._cache[full_key] = value
    
    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()

class RedisaCacheManager:
    """Redis cache manager (placeholder - would need redis-py)"""
    
    def __init__(self, cache_config):
        self.config = cache_config
        logger.warning("Redis cache not implemented - using memory cache")
        self._fallback = MemoryCacheManager(cache_config)
    
    def get(self, key: str) -> Any:
        return self._fallback.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._fallback.set(key, value)
    
    def clear(self) -> None:
        self._fallback.clear()

class NullCacheManager:
    """Null cache manager for disabled caching"""
    
    def get(self, key: str) -> Any:
        return None
    
    def set(self, key: str, value: Any) -> None:
        pass
    
    def clear(self) -> None:
        pass

class EnhancedHealthMonitor:
    """Enhanced health monitor with comprehensive system checks"""
    
    def __init__(self, config_manager: ConfigurationManager, database: Any, cache_manager: Any):
        self.config_manager = config_manager
        self.database = database
        self.cache_manager = cache_manager
    
    def get_health_status(self) -> dict:
        """Get comprehensive health status"""
        status = {
            'overall': 'healthy',
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'components': {}
        }
        
        # Check database
        try:
            if hasattr(self.database, 'execute_query'):
                result = self.database.execute_query("SELECT 1 as test")
                status['components']['database'] = {
                    'status': 'healthy' if not result.empty else 'unhealthy',
                    'type': self.config_manager.database_config.type
                }
            else:
                status['components']['database'] = {'status': 'unknown', 'type': 'mock'}
        except Exception as e:
            status['components']['database'] = {'status': 'unhealthy', 'error': str(e)}
            status['overall'] = 'degraded'
        
        # Check cache
        try:
            self.cache_manager.set('health_check', 'test')
            cache_result = self.cache_manager.get('health_check')
            status['components']['cache'] = {
                'status': 'healthy' if cache_result == 'test' else 'degraded',
                'type': self.config_manager.cache_config.type
            }
        except Exception as e:
            status['components']['cache'] = {'status': 'unhealthy', 'error': str(e)}
            status['overall'] = 'degraded'
        
        # Check configuration
        config_warnings = self.config_manager.validate_configuration()
        status['components']['configuration'] = {
            'status': 'healthy' if not config_warnings else 'warning',
            'warnings': config_warnings,
            'source': self.config_manager._config_source
        }
        
        return status

def get_configured_container_with_yaml() -> Container:
    """Get the global configured container with YAML support"""
    container = get_container()
    
    # Configure if not already configured
    if not container.has('config_manager'):
        configure_container_with_yaml(container)
    
    return container

# ============================================================================
# tests/test_yaml_configuration.py - NEW: Comprehensive configuration testing
"""
Comprehensive tests for YAML configuration system
"""

import os
import tempfile
import unittest
from pathlib import Path
from config.yaml_config import (
    ConfigurationManager, ConfigurationError,
    AppConfig, DatabaseConfig, SecurityConfig
)

class TestYAMLConfiguration(unittest.TestCase):
    """Test YAML configuration loading and validation"""
    
    def setUp(self):
        self.config_manager = ConfigurationManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configuration(self):
        """Test that default configuration is valid"""
        # Should not raise any exceptions
        self.assertIsInstance(self.config_manager.app_config, AppConfig)
        self.assertEqual(self.config_manager.app_config.port, 8050)
        self.assertTrue(self.config_manager.app_config.debug)
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution"""
        # Create test config with environment variables
        test_config = """
app:
  port: ${TEST_PORT:8080}
  debug: ${TEST_DEBUG:false}
  title: ${TEST_TITLE:Test App}

database:
  host: ${DB_HOST}
  password: ${DB_PASSWORD:default_password}
"""
        
        # Set environment variables
        os.environ['TEST_PORT'] = '9000'
        os.environ['TEST_DEBUG'] = 'true'
        os.environ['DB_HOST'] = 'test-db.example.com'
        # DB_PASSWORD not set - should use default
        
        # Write to temporary file
        config_path = Path(self.temp_dir) / 'test_config.yaml'
        config_path.write_text(test_config)
        
        # Load configuration
        self.config_manager.load_configuration(str(config_path))
        
        # Check substitution worked
        self.assertEqual(self.config_manager.app_config.port, 9000)
        self.assertTrue(self.config_manager.app_config.debug)
        self.assertEqual(self.config_manager.app_config.title, "Test App")
        self.assertEqual(self.config_manager.database_config.host, "test-db.example.com")
        self.assertEqual(self.config_manager.database_config.password, "default_password")
        
        # Clean up environment
        for var in ['TEST_PORT', 'TEST_DEBUG', 'DB_HOST']:
            os.environ.pop(var, None)
    
    def test_missing_required_environment_variable(self):
        """Test error when required environment variable is missing"""
        test_config = """
app:
  port: ${REQUIRED_PORT}
"""
        
        config_path = Path(self.temp_dir) / 'test_config.yaml'
        config_path.write_text(test_config)
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError):
            self.config_manager.load_configuration(str(config_path))
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Test invalid port
        self.config_manager.app_config.port = 99999999
        with self.assertRaises(ValueError):
            AppConfig(port=99999999)
        
        # Test invalid log level
        with self.assertRaises(ValueError):
            AppConfig(log_level="INVALID_LEVEL")
        
        # Test invalid database type
        with self.assertRaises(ValueError):
            DatabaseConfig(type="invalid_db_type")
    
    def test_production_warnings(self):
        """Test production configuration warnings"""
        # Set to production-like config
        self.config_manager.app_config.debug = False
        self.config_manager.security_config.secret_key = "dev-key-change-in-production"
        self.config_manager.app_config.host = "127.0.0.1"
        
        warnings = self.config_manager.validate_configuration()
        
        # Should have warnings about production settings
        self.assertTrue(any("secret key" in w.lower() for w in warnings))
        self.assertTrue(any("127.0.0.1" in w for w in warnings))
    
    def test_effective_configuration(self):
        """Test getting effective configuration"""
        effective = self.config_manager.get_effective_configuration()
        
        # Should have all sections
        required_sections = ['app', 'database', 'cache', 'security', 'analytics', 'monitoring']
        for section in required_sections:
            self.assertIn(section, effective)
        
        # Should have metadata
        self.assertIn('_meta', effective)
    
    def test_configuration_saving(self):
        """Test saving effective configuration"""
        output_path = Path(self.temp_dir) / 'effective_config.yaml'
        
        self.config_manager.save_effective_config(str(output_path))
        
        # File should exist and be valid YAML
        self.assertTrue(output_path.exists())
        
        import yaml
        with open(output_path) as f:
            saved_config = yaml.safe_load(f)
        
        # Should have redacted sensitive information
        self.assertEqual(saved_config['security']['secret_key'], '[REDACTED]')

def run_configuration_tests():
    """Run all configuration tests"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestYAMLConfiguration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

# ============================================================================
# validate_config.py - NEW: Standalone configuration validation script
"""
Standalone script to validate YAML configuration
Usage: python validate_config.py [config_file]
"""

def main():
    """Main validation script"""
    import sys
    
    print("🔍 YAML Configuration Validation")
    print("=" * 50)
    
    # Determine config file
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = None
        print("No config file specified, using environment detection...")
    
    try:
        # Create and load configuration
        config_manager = ConfigurationManager()
        config_manager.load_configuration(config_path)
        
        print(f"✅ Configuration loaded successfully")
        print(f"📂 Source: {config_manager._config_source or 'defaults'}")
        
        # Validate configuration
        warnings = config_manager.validate_configuration()
        
        if warnings:
            print(f"\n⚠️  Configuration Warnings ({len(warnings)}):")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print("✅ No configuration warnings")
        
        # Show effective configuration summary
        effective = config_manager.get_effective_configuration()
        print(f"\n📋 Configuration Summary:")
        print(f"  🌐 App: {effective['app']['host']}:{effective['app']['port']} (debug: {effective['app']['debug']})")
        print(f"  🗄️  Database: {effective['database']['type']}")
        print(f"  💾 Cache: {effective['cache']['type']}")
        print(f"  🔒 CORS: {'enabled' if effective['security']['cors_enabled'] else 'disabled'}")
        print(f"  📊 Max Query Records: {effective['analytics']['max_records_per_query']:,}")
        
        # Test environment variable substitution
        print(f"\n🌍 Environment Context:")
        print(f"  YOSAI_ENV: {os.getenv('YOSAI_ENV', 'not set')}")
        print(f"  YOSAI_CONFIG_FILE: {os.getenv('YOSAI_CONFIG_FILE', 'not set')}")
        
        print(f"\n🎉 Configuration validation completed successfully!")
        
        return True
        
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
        return False
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    print(f"\n📋 Next Steps:")
    if success:
        print("  1. Run your application: python app.py")
        print("  2. Check health endpoint: /health")
        print("  3. Review any configuration warnings above")
    else:
        print("  1. Fix configuration errors")
        print("  2. Set required environment variables")
        print("  3. Verify YAML syntax")
    
    sys.exit(0 if success else 1)

# Export key functions
__all__ = [
    'configure_container_with_yaml',
    'get_configured_container_with_yaml',
    'EnhancedHealthMonitor',
    'run_configuration_tests'
]