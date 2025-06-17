#!/usr/bin/env python3
"""
Test the fixed analytics service
"""

def test_fixed_analytics():
    """Test that the fixed analytics service works without timeout"""
    
    print("🧪 Testing Fixed Analytics Service...")
    
    try:
        # Import the fixed service registry
        from core.service_registry_fixed import get_configured_container_fixed
        
        print("✅ Successfully imported fixed service registry")
        
        # Get container
        container = get_configured_container_fixed()
        print(f"✅ Container created with {len(container._services)} services")
        
        # Test analytics service access (this should NOT timeout)
        print("🔍 Accessing analytics service...")
        analytics_service = container.get('analytics_service')
        print(f"✅ Analytics service accessed: {type(analytics_service).__name__}")
        
        # Test basic functionality
        print("🔍 Testing dashboard summary...")
        summary = analytics_service.get_dashboard_summary()
        print(f"✅ Dashboard summary works: {summary.get('total_events_30d', 0)} events")
        
        # Test other models
        print("🔍 Testing access model...")
        access_model = container.get('access_model')
        print(f"✅ Access model works: {type(access_model).__name__}")
        
        print("🎉 ALL TESTS PASSED - Analytics service is FIXED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_analytics()
    import sys
    sys.exit(0 if success else 1)
