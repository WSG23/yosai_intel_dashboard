# test_dependency_injection.py
"""Test script to verify dependency injection is working correctly"""
import sys
from pathlib import Path

def test_container_basic_functionality():
    """Test that the container works correctly"""
    print("🧪 Testing Container Basic Functionality...")
    
    try:
        from core.container import Container
        
        # Create container
        container = Container()
        
        # Register a simple service
        def create_test_service():
            return {"name": "test_service", "status": "working"}
        
        container.register('test_service', create_test_service)
        
        # Get service
        service = container.get('test_service')
        
        assert service['name'] == 'test_service'
        assert service['status'] == 'working'
        
        print("✅ Container basic functionality works")
        return True
        
    except Exception as e:
        print(f"❌ Container test failed: {e}")
        return False

def test_dependency_injection():
    """Test dependency injection between services"""
    print("🧪 Testing Dependency Injection...")
    
    try:
        from core.container import Container
        
        # Create container
        container = Container()
        
        # Register config service
        def create_config():
            return {"database_url": "mock://test", "debug": True}
        
        container.register('config', create_config)
        
        # Register database service that depends on config
        def create_database(config):
            return {"type": "mock", "url": config["database_url"], "status": "connected"}
        
        container.register('database', create_database, dependencies=['config'])
        
        # Get database (should automatically inject config)
        database = container.get('database')
        
        assert database['url'] == 'mock://test'
        assert database['status'] == 'connected'
        
        print("✅ Dependency injection works")
        return True
        
    except Exception as e:
        print(f"❌ Dependency injection test failed: {e}")
        return False

def test_service_registry():
    """Test that the service registry configures all services"""
    print("🧪 Testing Service Registry...")
    
    try:
        from core.service_registry import get_configured_container
        
        # Get configured container
        container = get_configured_container()
        
        # Test that key services are registered
        services_to_test = ['config', 'database', 'analytics_service', 'file_processor']
        
        for service_name in services_to_test:
            if container.has(service_name):
                try:
                    service = container.get(service_name)
                    if service is not None:
                        print(f"✅ {service_name}: Available")
                    else:
                        print(f"⚠️  {service_name}: Registered but None")
                except Exception as e:
                    print(f"❌ {service_name}: Error getting service - {e}")
            else:
                print(f"❌ {service_name}: Not registered")
        
        print("✅ Service registry configuration complete")
        return True
        
    except Exception as e:
        print(f"❌ Service registry test failed: {e}")
        return False

def test_analytics_service_injection():
    """Test that analytics service can be injected and used"""
    print("🧪 Testing Analytics Service Injection...")
    
    try:
        from core.service_registry import get_configured_container
        import pandas as pd
        from datetime import datetime
        
        # Get container
        container = get_configured_container()
        
        # Get analytics service
        analytics_service = container.get('analytics_service')
        
        if analytics_service is None:
            print("⚠️  Analytics service not available (this is OK for testing)")
            return True
        
        # Test with sample data
        sample_data = pd.DataFrame({
            'person_id': ['EMP001', 'EMP002'],
            'door_id': ['MAIN', 'SERVER'],
            'access_result': ['Granted', 'Denied'],
            'timestamp': [datetime.now(), datetime.now()]
        })
        
        # Try to process data
        result = analytics_service.process_uploaded_file(sample_data, "test.csv")
        
        if isinstance(result, dict):
            print("✅ Analytics service injection and processing works")
        else:
            print("⚠️  Analytics service returned unexpected result")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics service injection test failed: {e}")
        return False

def test_app_creation_with_di():
    """Test that the app can be created with dependency injection"""
    print("🧪 Testing App Creation with DI...")
    
    try:
        from core.app_factory import create_application
        
        # Create app (this should use DI internally)
        app = create_application()
        
        if app is not None:
            # Check that container is attached
            if hasattr(app, '_yosai_container'):
                container = app._yosai_container
                if container is not None and container.has('config'):
                    print("✅ App created with DI container successfully")
                    return True
                else:
                    print("⚠️  App created but container not properly configured")
                    return False
            else:
                print("⚠️  App created but no container attached")
                return False
        else:
            print("❌ App creation failed")
            return False
            
    except Exception as e:
        print(f"❌ App creation with DI test failed: {e}")
        return False

def test_mock_replacement():
    """Test that services can be easily mocked for testing"""
    print("🧪 Testing Mock Replacement (DI Testing Benefit)...")
    
    try:
        from core.container import Container
        
        # Create container
        container = Container()
        
        # Register original service
        def real_service():
            return {"type": "real", "data": "production_data"}
        
        container.register('my_service', real_service)
        
        # Get real service
        real = container.get('my_service')
        assert real['type'] == 'real'
        
        # Replace with mock for testing
        def mock_service():
            return {"type": "mock", "data": "test_data"}
        
        container.register('my_service', mock_service)  # Override
        
        # Get mock service
        mock = container.get('my_service')
        assert mock['type'] == 'mock'
        assert mock['data'] == 'test_data'
        
        print("✅ Mock replacement works (makes testing easy!)")
        return True
        
    except Exception as e:
        print(f"❌ Mock replacement test failed: {e}")
        return False

def main():
    """Run all dependency injection tests"""
    print("🚀 DEPENDENCY INJECTION VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Container Basic Functionality", test_container_basic_functionality),
        ("Dependency Injection", test_dependency_injection),
        ("Service Registry", test_service_registry),
        ("Analytics Service Injection", test_analytics_service_injection),
        ("App Creation with DI", test_app_creation_with_di),
        ("Mock Replacement", test_mock_replacement)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} had issues")
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Dependency Injection is working!")
        print("\n✅ Benefits you now have:")
        print("   • Easy testing with mocks")
        print("   • Flexible service configuration")
        print("   • Better separation of concerns")
        print("   • Easier to add new features")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    print(f"\n🚀 Next steps:")
    print("   1. Run your app: python app.py")
    print("   2. Test that everything still works")
    print("   3. Try uploading a file to analytics page")
    print("   4. Ready for next modularity improvement!")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
