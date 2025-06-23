#!/usr/bin/env python3
"""
Test script for the fixed ConfigurationManager implementation
Tests the main dashboard implementation with proper error handling
"""
import sys
import os
import logging
from typing import Dict, Any, Tuple
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_configuration_manager_fix() -> Tuple[bool, str]:
    """Test the fixed ConfigurationManager.from_environment method"""
    try:
        from config.yaml_config import ConfigurationManager
        
        # Test the from_environment class method
        config_manager = ConfigurationManager.from_environment()
        
        if config_manager is None:
            return False, "from_environment returned None"
        
        # Test that it has the expected attributes
        required_attrs = [
            'app_config', 'database_config', 'cache_config', 
            'security_config', 'analytics_config', 'monitoring_config'
        ]
        
        for attr in required_attrs:
            if not hasattr(config_manager, attr):
                return False, f"Missing attribute: {attr}"
        
        # Test configuration validation
        warnings = config_manager.validate_configuration()
        
        return True, f"ConfigurationManager.from_environment() works! Found {len(warnings)} configuration warnings."
        
    except Exception as e:
        return False, f"Error: {e}"

def test_service_registry_integration() -> Tuple[bool, str]:
    """Test service registry with fixed configuration"""
    try:
        from core.service_registry import get_configured_container_with_yaml
        
        # This should now work without the from_environment error
        container = get_configured_container_with_yaml()
        
        if container is None:
            return False, "Container creation failed"
        
        # Test that config_manager service is registered
        if not container.has('config_manager'):
            return False, "config_manager service not registered"
        
        # Test that we can retrieve the config manager
        config_manager = container.get('config_manager')
        if config_manager is None:
            return False, "config_manager service is None"
        
        return True, f"Service registry integration works! Container has {len(container._services)} services."
        
    except Exception as e:
        return False, f"Error: {e}"

def test_main_dashboard_implementation() -> Tuple[bool, str]:
    """Test the main dashboard implementation like the original error"""
    try:
        from core.service_registry import get_configured_container_with_yaml
        
        # This is the exact test that was failing
        container = get_configured_container_with_yaml()
        
        if container is None:
            return False, "Container creation failed"
        
        print(f'✅ Container: {type(container)}')
        
        # Test health check
        if container.has('health_monitor'):
            health_monitor = container.get('health_monitor')
            health = health_monitor.health_check()
            print(f'📊 Container status: {health["overall"]}')
            print(f'🔧 Services available: {len(health["services"])}')
        else:
            # Fallback health check
            health = container.health_check()
            print(f'📊 Container status: {health["status"]}')
            print(f'🔧 Services available: {len(health["services"])}')
        
        return True, "Main dashboard implementation test passed!"
        
    except Exception as e:
        return False, f"Error: {e}"

def test_modular_architecture() -> Tuple[bool, str]:
    """Test that the modular architecture principles are working"""
    try:
        # Test 1: Configuration module isolation
        from config.yaml_config import ConfigurationManager
        config = ConfigurationManager.from_environment()
        
        # Test 2: Service registry module isolation  
        from core.service_registry import create_config_manager, test_container_configuration
        test_config = create_config_manager()
        
        # Test 3: Container module isolation
        from core.dependency_container import ServiceContainer
        container = ServiceContainer()
        
        # Test 4: Integration test
        test_result = test_container_configuration()
        
        if not test_result.get('success', False):
            return False, f"Integration test failed: {test_result.get('error', 'Unknown error')}"
        
        return True, f"Modular architecture working! Test result: {test_result['config_manager_type']}"
        
    except Exception as e:
        return False, f"Error: {e}"

def test_error_isolation() -> Tuple[bool, str]:
    """Test that modules can be tested in isolation"""
    isolated_tests = []
    
    # Test 1: Can import config module independently
    try:
        from config.yaml_config import ConfigurationManager
        config = ConfigurationManager()  # Should work without dependencies
        isolated_tests.append("✅ Config module isolated")
    except Exception as e:
        isolated_tests.append(f"❌ Config module: {e}")
    
    # Test 2: Can import container module independently
    try:
        from core.dependency_container import ServiceContainer
        container = ServiceContainer()  # Should work without dependencies
        isolated_tests.append("✅ Container module isolated")
    except Exception as e:
        isolated_tests.append(f"❌ Container module: {e}")
    
    # Test 3: Can import service registry module independently
    try:
        from core.service_registry import MockDatabaseConnection
        mock_db = MockDatabaseConnection()  # Should work without dependencies
        isolated_tests.append("✅ Service registry module isolated")
    except Exception as e:
        isolated_tests.append(f"❌ Service registry module: {e}")
    
    success_count = sum(1 for test in isolated_tests if test.startswith("✅"))
    total_tests = len(isolated_tests)
    
    return (
        success_count == total_tests,
        f"Isolation test: {success_count}/{total_tests} passed\n" + "\n".join(isolated_tests)
    )

def run_comprehensive_test_suite() -> None:
    """Run all tests and provide detailed feedback"""
    print("🧪 Testing Fixed ConfigurationManager Implementation...")
    print("=" * 60)
    
    tests = [
        ("ConfigurationManager.from_environment Fix", test_configuration_manager_fix),
        ("Service Registry Integration", test_service_registry_integration), 
        ("Main Dashboard Implementation", test_main_dashboard_implementation),
        ("Modular Architecture", test_modular_architecture),
        ("Error Isolation", test_error_isolation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        try:
            success, message = test_func()
            results.append((test_name, success, message))
            
            if success:
                print(f"✅ PASSED: {message}")
            else:
                print(f"❌ FAILED: {message}")
                
        except Exception as e:
            results.append((test_name, False, f"Test crashed: {e}"))
            print(f"💥 CRASHED: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ ConfigurationManager.from_environment() method is working")
        print("✅ Service registry integration is working") 
        print("✅ Main dashboard implementation is working")
        print("✅ Modular architecture principles are satisfied")
        print("✅ Error isolation is working properly")
        
        print(f"\n🚀 Your application should now start without the from_environment error!")
        
    else:
        print(f"\n⚠️  {total - passed} tests failed. Issues to address:")
        for test_name, success, message in results:
            if not success:
                print(f"   • {test_name}: {message}")

def debug_environment() -> None:
    """Debug the current environment setup"""
    print("\n🔧 Environment Debug Information")
    print("=" * 60)
    
    try:
        from core.service_registry import debug_configuration_loading
        debug_info = debug_configuration_loading()
        
        print(f"📁 Config files found: {debug_info['config_files_found']}")
        print(f"🌍 Environment variables:")
        for var, value in debug_info['environment_vars'].items():
            print(f"   {var}: {value}")
        print(f"📦 Import status:")
        for module, status in debug_info['import_status'].items():
            print(f"   {module}: {status}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing main dashboard implementation...")
    
    # Run the exact test that was failing in the original output
    try:
        from core.service_registry import get_configured_container_with_yaml
        container = get_configured_container_with_yaml()
        print(f'✅ Container: {type(container)}')
        
        # Test health check
        health = container.health_check()
        print(f'📊 Container status: {health["status"]}')
        print(f'🔧 Services available: {len(health["services"])}')
        
        print("\n🎉 SUCCESS! The from_environment error has been fixed!")
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print("\n🔧 Running comprehensive test suite to diagnose...")
        
        # Run comprehensive tests if the simple test fails
        run_comprehensive_test_suite()
        debug_environment()
    
    # Always run comprehensive tests for verification
    print("\n" + "=" * 60)
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    run_comprehensive_test_suite()