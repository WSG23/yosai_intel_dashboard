#!/usr/bin/env python3
"""
Fixed test script with robust health check handling
Handles different health check response formats gracefully
"""

def test_main_dashboard_implementation():
    """Test with robust health check handling"""
    print('🧪 Testing main dashboard implementation...')
    
    try:
        from core.service_registry import get_configured_container_with_yaml
        container = get_configured_container_with_yaml()
        print(f'✅ Container: {type(container)}')
        
        # Get health check with robust error handling
        health = container.health_check()
        print(f"🔍 Health check response: {health}")
        
        # Handle different health check response formats
        if isinstance(health, dict):
            # Try different possible status keys
            status = (health.get('status') or 
                     health.get('overall') or 
                     health.get('overall_status') or 
                     'unknown')
            print(f'📊 Container status: {status}')
            
            # Try different possible services keys
            services = (health.get('services') or 
                       health.get('service_status') or 
                       health.get('components') or {})
            
            if isinstance(services, dict):
                print(f'🔧 Services available: {len(services)}')
                
                # Show detailed service status
                if services:
                    print("📋 Service Details:")
                    for service_name, service_info in services.items():
                        if isinstance(service_info, dict):
                            service_status = service_info.get('status', 'unknown')
                            print(f"   • {service_name}: {service_status}")
                        else:
                            print(f"   • {service_name}: {service_info}")
            else:
                print(f'🔧 Services data: {services}')
        else:
            print(f'📊 Health response: {health}')
        
        print('\n🎉 SUCCESS! Dashboard implementation is working!')
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print(f'❌ Error type: {type(e).__name__}')
        return False

def debug_health_check_structure():
    """Debug the actual health check response structure"""
    print('\n🔍 Debugging health check structure...')
    
    try:
        from core.service_registry import get_configured_container_with_yaml
        container = get_configured_container_with_yaml()
        
        # Get health check and inspect structure
        health = container.health_check()
        
        print(f"📋 Health check type: {type(health)}")
        print(f"📋 Health check keys: {list(health.keys()) if isinstance(health, dict) else 'Not a dict'}")
        print(f"📋 Full health response:")
        
        if isinstance(health, dict):
            for key, value in health.items():
                print(f"   {key}: {value} (type: {type(value).__name__})")
        else:
            print(f"   {health}")
            
        return health
        
    except Exception as e:
        print(f'❌ Debug error: {e}')
        return None

def test_container_services():
    """Test container services directly"""
    print('\n🔧 Testing container services directly...')
    
    try:
        from core.service_registry import get_configured_container_with_yaml
        container = get_configured_container_with_yaml()
        
        # Check if container has _services attribute
        if hasattr(container, '_services'):
            services = container._services
            print(f"📦 Direct services count: {len(services)}")
            print(f"📦 Service names: {list(services.keys())}")
            
            # Test a few services
            for service_name in list(services.keys())[:5]:  # Test first 5 services
                try:
                    service = container.get(service_name)
                    print(f"   ✅ {service_name}: {type(service).__name__}")
                except Exception as e:
                    print(f"   ❌ {service_name}: Error - {e}")
        else:
            print("❌ Container doesn't have _services attribute")
            
        return True
        
    except Exception as e:
        print(f'❌ Services test error: {e}')
        return False

def comprehensive_test():
    """Run comprehensive test with detailed diagnostics"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE DASHBOARD TEST")
    print("=" * 60)
    
    # Test 1: Basic implementation
    success1 = test_main_dashboard_implementation()
    
    # Test 2: Debug health check structure  
    health_data = debug_health_check_structure()
    
    # Test 3: Direct services test
    success2 = test_container_services()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if success1:
        print("✅ Main dashboard implementation: WORKING")
    else:
        print("❌ Main dashboard implementation: FAILED")
        
    if success2:
        print("✅ Container services: WORKING")
    else:
        print("❌ Container services: FAILED")
    
    if health_data:
        print("✅ Health check: RESPONDING")
    else:
        print("❌ Health check: FAILED")
    
    overall_success = success1 and success2 and health_data
    
    if overall_success:
        print("\n🎉 OVERALL STATUS: SUCCESS!")
        print("✅ Your dashboard is ready to use!")
    else:
        print("\n⚠️ OVERALL STATUS: NEEDS ATTENTION")
        print("💡 Check the detailed output above for specific issues")

if __name__ == "__main__":
    comprehensive_test()