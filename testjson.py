#!/usr/bin/env python3
"""
Test script to verify the fixed JSON plugin works properly
Run this to confirm your modular plugin architecture is working
"""

import sys
import json
import pandas as pd
from datetime import datetime

def test_plugin_directly():
    """Test the JSON plugin in isolation"""
    print("🧪 Testing JSON Plugin Directly...")
    print("=" * 40)
    
    try:
        # Import the fixed plugin
        from core.json_serialization_plugin import JsonSerializationPlugin, JsonSerializationConfig
        from core.container import Container
        
        # Create plugin and container
        container = Container()
        plugin = JsonSerializationPlugin()
        
        config = {
            'enabled': True,
            'max_dataframe_rows': 1000,
            'fallback_to_repr': True,
            'auto_wrap_callbacks': True
        }
        
        # Test plugin lifecycle
        print("1. Loading plugin...")
        success = plugin.load(container, config)
        assert success, "Plugin load failed"
        print("   ✅ Plugin loaded")
        
        print("2. Configuring plugin...")
        success = plugin.configure(config)
        assert success, "Plugin configure failed"
        print("   ✅ Plugin configured")
        
        print("3. Starting plugin...")
        success = plugin.start()
        assert success, "Plugin start failed"
        print("   ✅ Plugin started")
        
        # Test LazyString handling
        print("4. Testing LazyString handling...")
        try:
            from flask_babel import lazy_gettext as _l
            
            test_data = {
                'lazy_str': _l('Test message'),
                'nested': {
                    'lazy_nested': _l('Nested lazy'),
                    'normal': 'Normal string'
                },
                'lazy_list': [_l('Item 1'), _l('Item 2')]
            }
            
            # This should work without errors
            sanitized = plugin.serialization_service.sanitize_for_transport(test_data)
            json_str = json.dumps(sanitized)
            print(f"   ✅ LazyString handling works: {len(json_str)} chars")
            
        except ImportError:
            print("   ⚠️  Flask-Babel not available, testing with mock LazyString")
            
            class MockLazyString:
                def __init__(self, text):
                    self._func = lambda: text
                    self._args = ()
                def __str__(self):
                    return self._func()
            
            mock_data = {
                'mock_lazy': MockLazyString('Mock lazy string'),
                'normal': 'Normal string'
            }
            
            sanitized = plugin.serialization_service.sanitize_for_transport(mock_data)
            json_str = json.dumps(sanitized)
            print(f"   ✅ Mock LazyString handling works: {len(json_str)} chars")
        
        # Test DataFrame handling
        print("5. Testing DataFrame handling...")
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        sanitized_df = plugin.serialization_service.sanitize_for_transport(df)
        json_str = json.dumps(sanitized_df)
        print(f"   ✅ DataFrame handling works: {len(json_str)} chars")
        
        # Test health check
        print("6. Testing health check...")
        health = plugin.health_check()
        assert health['healthy'], f"Plugin not healthy: {health}"
        print("   ✅ Plugin health check passed")
        
        print("\n🎉 Plugin tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_integration():
    """Test that the app properly loads the plugin"""
    print("\n🔗 Testing App Integration...")
    print("=" * 40)
    
    try:
        print("1. Creating app with plugin...")
        from core.app_factory import create_application
        
        app = create_application()
        
        if app is None:
            print("   ❌ App creation failed")
            return False
        
        print("   ✅ App created")
        
        # Check if plugin is attached
        print("2. Checking plugin integration...")
        if hasattr(app, '_yosai_json_plugin'):
            plugin = app._yosai_json_plugin
            print("   ✅ JSON plugin attached to app")
            
            # Test plugin health
            health = plugin.health_check()
            if health.get('healthy', False):
                print("   ✅ Plugin is healthy in app context")
                return True
            else:
                print(f"   ❌ Plugin not healthy in app: {health}")
                return False
        else:
            print("   ❌ JSON plugin not found on app")
            return False
            
    except Exception as e:
        print(f"   ❌ App integration test failed: {e}")
        return False

def test_global_json_patch():
    """Test that the global JSON patch is working"""
    print("\n🌐 Testing Global JSON Patch...")
    print("=" * 40)
    
    try:
        # First create the plugin to apply patches
        from core.json_serialization_plugin import JsonSerializationPlugin
        plugin = JsonSerializationPlugin()
        plugin.start()  # This applies global patches
        
        print("1. Testing basic JSON serialization...")
        test_obj = {'normal': 'data', 'number': 42}
        result = json.dumps(test_obj)
        print(f"   ✅ Basic JSON works: {len(result)} chars")
        
        print("2. Testing problematic objects...")
        problematic = {
            'function': lambda x: x,
            'datetime': datetime.now(),
            'pandas_df': pd.DataFrame({'X': [1, 2]})
        }
        
        # This should work now due to global patch
        result = json.dumps(problematic)
        print(f"   ✅ Problematic objects handled: {len(result)} chars")
        
        print("3. Testing LazyString with global patch...")
        try:
            from flask_babel import lazy_gettext as _l
            lazy_obj = {'message': _l('Test message')}
            result = json.dumps(lazy_obj)
            print(f"   ✅ LazyString handled globally: {len(result)} chars")
        except ImportError:
            print("   ⚠️  Flask-Babel not available for LazyString test")
        
        print("   ✅ Global JSON patch working!")
        return True
        
    except Exception as e:
        print(f"   ❌ Global patch test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏯 YŌSAI JSON PLUGIN VERIFICATION")
    print("Testing your modular plugin architecture...")
    print("=" * 50)
    
    # Run all tests
    plugin_test = test_plugin_directly()
    app_test = test_app_integration()
    global_test = test_global_json_patch()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Plugin Direct Test: {'✅ PASS' if plugin_test else '❌ FAIL'}")
    print(f"   App Integration:    {'✅ PASS' if app_test else '❌ FAIL'}")
    print(f"   Global JSON Patch:  {'✅ PASS' if global_test else '❌ FAIL'}")
    
    if plugin_test and app_test and global_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your modular JSON plugin architecture is working!")
        print("✅ LazyString serialization issues are resolved!")
        print("\n🚀 You can now run: python3 app.py")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the error messages above.")
        sys.exit(1)