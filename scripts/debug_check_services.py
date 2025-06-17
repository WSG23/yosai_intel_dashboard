#!/usr/bin/env python3
"""
Debug Service Checker - Simple Version
=====================================

A simplified version to debug what's happening with the service checker.
"""

import sys
import traceback
import time
from datetime import datetime

def debug_print(message):
    """Print debug messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] DEBUG: {message}")
    sys.stdout.flush()

def test_di_container():
    """Test DI container functionality"""
    debug_print("Testing DI Container...")
    try:
        from core.service_registry import get_configured_container
        debug_print("Successfully imported get_configured_container")
        
        container = get_configured_container()
        debug_print(f"Container created: {type(container).__name__}")
        
        # Try to get list of services
        if hasattr(container, 'list_services'):
            services = container.list_services()
            debug_print(f"Services available: {len(services)} - {services[:5]}")
        elif hasattr(container, '_services'):
            services = list(container._services.keys())
            debug_print(f"Services in _services: {len(services)} - {services[:5]}")
        else:
            debug_print("No obvious way to list services")
            
        # Try health check
        if hasattr(container, 'health_check'):
            health = container.health_check()
            debug_print(f"Health check result: {health.get('status', 'unknown')}")
        else:
            debug_print("No health_check method available")
            
        return True, "DI Container working"
        
    except Exception as e:
        debug_print(f"DI Container error: {e}")
        traceback.print_exc()
        return False, str(e)

def test_database():
    """Test database functionality"""
    debug_print("Testing Database...")
    try:
        from config.database_manager import DatabaseManager, DatabaseConfig
        debug_print("Successfully imported DatabaseManager")
        
        config = DatabaseManager.from_environment()
        debug_print(f"Config created: {config.db_type}")
        
        connection = DatabaseManager.create_connection(config)
        debug_print(f"Connection created: {type(connection).__name__}")
        
        # Try a simple query
        result = connection.execute_query("SELECT 1 as test")
        debug_print(f"Query result type: {type(result).__name__}")
        
        connection.close()
        debug_print("Connection closed successfully")
        
        return True, "Database working"
        
    except Exception as e:
        debug_print(f"Database error: {e}")
        traceback.print_exc()
        return False, str(e)

def test_configuration():
    """Test configuration functionality"""
    debug_print("Testing Configuration...")
    try:
        from config.yaml_config import ConfigurationManager
        debug_print("Successfully imported ConfigurationManager")
        
        config_manager = ConfigurationManager()
        debug_print("ConfigurationManager created")
        
        config_manager.load_configuration()
        debug_print("Configuration loaded")
        
        debug_print(f"Environment: {getattr(config_manager, 'environment', 'unknown')}")
        debug_print(f"Has app_config: {hasattr(config_manager, 'app_config')}")
        
        return True, "Configuration working"
        
    except Exception as e:
        debug_print(f"Configuration error: {e}")
        traceback.print_exc()
        return False, str(e)

def test_analytics_service():
    """Test analytics service functionality"""
    debug_print("Testing Analytics Service...")
    try:
        from core.service_registry import get_configured_container
        debug_print("Getting container for analytics service")
        
        container = get_configured_container()
        debug_print("Container obtained")
        
        # Try to get analytics service
        analytics_service = None
        
        if hasattr(container, 'get_optional'):
            analytics_service = container.get_optional('analytics_service')
            debug_print(f"get_optional result: {analytics_service is not None}")
        elif hasattr(container, 'get'):
            try:
                analytics_service = container.get('analytics_service')
                debug_print(f"get result: {analytics_service is not None}")
            except Exception as e:
                debug_print(f"get method failed: {e}")
        
        if analytics_service:
            debug_print(f"Analytics service type: {type(analytics_service).__name__}")
            # Try to call a method
            try:
                summary = analytics_service.get_dashboard_summary()
                debug_print(f"Dashboard summary successful: {type(summary).__name__}")
                return True, "Analytics service working"
            except Exception as e:
                debug_print(f"Dashboard summary failed: {e}")
                return True, f"Analytics service available but method failed: {e}"
        else:
            debug_print("Analytics service not available in container")
            return False, "Analytics service not found in container"
            
    except Exception as e:
        debug_print(f"Analytics service error: {e}")
        traceback.print_exc()
        return False, str(e)

def run_simple_checks():
    """Run simple service checks"""
    debug_print("=" * 50)
    debug_print("SIMPLE SERVICE CHECKER - DEBUG MODE")
    debug_print("=" * 50)
    
    tests = [
        ("DI Container", test_di_container),
        ("Database", test_database),
        ("Configuration", test_configuration),
        ("Analytics Service", test_analytics_service),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        debug_print(f"\n--- Testing {test_name} ---")
        try:
            start_time = time.time()
            success, message = test_func()
            end_time = time.time()
            
            results[test_name] = {
                'success': success,
                'message': message,
                'time_ms': round((end_time - start_time) * 1000, 2)
            }
            
            status = "✅ PASS" if success else "❌ FAIL"
            debug_print(f"{status}: {message} ({results[test_name]['time_ms']}ms)")
            
        except Exception as e:
            debug_print(f"💥 CRASH: {e}")
            traceback.print_exc()
            results[test_name] = {
                'success': False,
                'message': f"Test crashed: {e}",
                'time_ms': 0
            }
    
    # Print summary
    debug_print("\n" + "=" * 50)
    debug_print("SUMMARY")
    debug_print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"{status} {test_name}: {result['message']} ({result['time_ms']}ms)")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r['success'])
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All services are working!")
    else:
        print("⚠️  Some services need attention")
    
    return results

def main():
    """Main function"""
    try:
        debug_print("Starting debug service checker...")
        results = run_simple_checks()
        debug_print("Debug checker completed successfully")
        
        # Exit with appropriate code
        all_passed = all(r['success'] for r in results.values())
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        debug_print(f"Main function crashed: {e}")
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()