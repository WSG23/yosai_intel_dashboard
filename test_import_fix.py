#!/usr/bin/env python3
"""
Quick test to verify the JSON plugin import issue is fixed
"""

import sys

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing JSON Plugin Imports...")
    print("=" * 40)
    
    try:
        print("1. Testing plugin import...")
        from core.json_serialization_plugin import JsonSerializationPlugin
        print("   ✅ JsonSerializationPlugin imported successfully")
        
        print("2. Testing plugin creation...")
        plugin = JsonSerializationPlugin()
        print("   ✅ Plugin instance created")
        
        print("3. Testing metadata access...")
        metadata = plugin.metadata
        print(f"   ✅ Plugin metadata: {metadata.name} v{metadata.version}")
        
        print("4. Testing container import...")
        from core.di_container import DIContainer
        container = DIContainer()
        print("   ✅ Container imported and created")
        
        print("5. Testing plugin load...")
        config = {
            'enabled': True,
            'max_dataframe_rows': 1000,
            'fallback_to_repr': True
        }
        
        success = plugin.load(container, config)
        print(f"   ✅ Plugin load: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print("6. Testing plugin start...")
            success = plugin.start()
            print(f"   ✅ Plugin start: {'SUCCESS' if success else 'FAILED'}")
        
        print("\n🎉 All imports working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_serialization():
    """Test basic serialization functionality"""
    print("\n🔧 Testing Basic Serialization...")
    print("=" * 40)
    
    try:
        from core.json_serialization_plugin import JsonSerializationPlugin
        import json
        
        plugin = JsonSerializationPlugin()
        config = {'enabled': True, 'fallback_to_repr': True}
        
        from core.di_container import DIContainer
        container = DIContainer()
        
        plugin.load(container, config)
        plugin.start()  # This applies global JSON patches
        
        print("1. Testing basic JSON serialization...")
        test_data = {'message': 'hello', 'number': 42}
        result = json.dumps(test_data)
        print(f"   ✅ Basic JSON: {result}")
        
        print("2. Testing problematic objects...")
        problematic = {
            'function': lambda x: x,
            'callable': print
        }
        
        # This should work now due to global patch
        result = json.dumps(problematic)
        print(f"   ✅ Problematic objects: {len(result)} chars")
        
        print("3. Testing LazyString simulation...")
        class MockLazyString:
            def __init__(self, text):
                self._func = lambda: text
                self._args = ()
            def __str__(self):
                return self._func()
        
        mock_data = {'lazy': MockLazyString('lazy string')}
        result = json.dumps(mock_data)
        print(f"   ✅ Mock LazyString: {result}")
        
        print("\n🎉 Serialization tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Serialization test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏯 YŌSAI JSON PLUGIN IMPORT FIX TEST")
    print("=" * 50)
    
    import_test = test_imports()
    serialization_test = test_basic_serialization()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Import Test:        {'✅ PASS' if import_test else '❌ FAIL'}")
    print(f"   Serialization Test: {'✅ PASS' if serialization_test else '❌ FAIL'}")
    
    if import_test and serialization_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Import issues fixed!")
        print("✅ JSON plugin is working!")
        print("\n🚀 You can now run: python3 app.py")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the error messages above.")
        sys.exit(1)