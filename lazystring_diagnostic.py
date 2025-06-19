#!/usr/bin/env python3
"""
LazyString Error Diagnostic
Identifies exactly where LazyString serialization errors occur

Run this to pinpoint the exact source of LazyString errors.
"""

import os
import sys
import json
import traceback
from pathlib import Path

def setup_minimal_env():
    """Setup minimal environment"""
    os.environ.update({
        'WTF_CSRF_ENABLED': 'False',
        'SECRET_KEY': 'diagnostic-key',
        'FLASK_ENV': 'development',
        'YOSAI_ENV': 'development',
        'AUTH0_CLIENT_ID': 'diagnostic-id',
        'AUTH0_CLIENT_SECRET': 'diagnostic-secret',
        'AUTH0_DOMAIN': 'diagnostic.auth0.com'
    })

def test_json_baseline():
    """Test basic JSON functionality"""
    print("🧪 Testing JSON baseline...")
    
    try:
        # Basic types
        basic_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        result = json.dumps(basic_data)
        print(f"✅ Basic JSON works: {len(result)} chars")
        return True
        
    except Exception as e:
        print(f"❌ Basic JSON failed: {e}")
        return False

def test_flask_babel_lazystring():
    """Test Flask-Babel LazyString specifically"""
    print("🧪 Testing Flask-Babel LazyString...")
    
    try:
        from flask_babel import lazy_gettext as _l
        
        # Create LazyString
        lazy_str = _l("Test message")
        print(f"LazyString type: {type(lazy_str)}")
        print(f"LazyString value: {lazy_str}")
        print(f"LazyString str(): {str(lazy_str)}")
        
        # Try to serialize
        try:
            result = json.dumps({"message": lazy_str})
            print(f"✅ LazyString JSON works: {result}")
            return True
        except Exception as e:
            print(f"❌ LazyString JSON failed: {e}")
            print(f"Error type: {type(e)}")
            return False
        
    except ImportError:
        print("❌ Flask-Babel not available")
        return False
    except Exception as e:
        print(f"❌ Flask-Babel test failed: {e}")
        return False

def test_app_creation():
    """Test app creation and identify where LazyString errors occur"""
    print("🧪 Testing app creation for LazyString errors...")
    
    try:
        # Patch JSON to track serialization attempts
        original_default = json.JSONEncoder.default
        serialization_attempts = []
        
        def tracking_json_handler(self, obj):
            obj_info = {
                'type': str(type(obj)),
                'value': str(obj)[:100],  # First 100 chars
                'module': getattr(type(obj), '__module__', 'unknown')
            }
            serialization_attempts.append(obj_info)
            
            # Check for LazyString
            if 'LazyString' in obj_info['type']:
                print(f"🔍 LazyString detected: {obj_info}")
                return str(obj)  # Convert to string
            
            # Try original handler
            try:
                return original_default(self, obj)
            except:
                print(f"🔍 Serialization failed for: {obj_info}")
                return str(obj)
        
        # Apply tracking patch
        json.JSONEncoder.default = tracking_json_handler
        
        # Try to create app
        from core.app_factory import create_application
        app = create_application()
        
        # Report findings
        print(f"\n📊 Serialization Analysis:")
        print(f"Total serialization attempts: {len(serialization_attempts)}")
        
        lazystring_attempts = [a for a in serialization_attempts if 'LazyString' in a['type']]
        if lazystring_attempts:
            print(f"LazyString attempts: {len(lazystring_attempts)}")
            for attempt in lazystring_attempts[:5]:  # Show first 5
                print(f"  - Type: {attempt['type']}")
                print(f"    Value: {attempt['value']}")
                print(f"    Module: {attempt['module']}")
        
        # Restore original handler
        json.JSONEncoder.default = original_default
        
        if app:
            print("✅ App creation succeeded with tracking")
            return True
        else:
            print("❌ App creation failed")
            return False
        
    except Exception as e:
        print(f"❌ App creation test failed: {e}")
        traceback.print_exc()
        return False

def test_specific_modules():
    """Test specific modules that might contain LazyString"""
    print("🧪 Testing specific modules...")
    
    modules_to_test = [
        'components.map_panel',
        'components.bottom_panel',
        'components.incident_alerts_panel',
        'components.weak_signal_panel',
        'core.app_factory',
        'pages.deep_analytics'
    ]
    
    problematic_modules = []
    
    for module_name in modules_to_test:
        try:
            print(f"Testing {module_name}...")
            module = __import__(module_name, fromlist=[''])
            
            # Try to serialize module attributes
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(module, attr_name)
                        json.dumps({"test": attr_value})
                    except Exception as e:
                        if 'LazyString' in str(e):
                            problematic_modules.append(f"{module_name}.{attr_name}")
                            print(f"  ❌ LazyString in {attr_name}: {e}")
            
            print(f"  ✅ {module_name} checked")
            
        except Exception as e:
            print(f"  ❌ {module_name} failed: {e}")
    
    if problematic_modules:
        print(f"\n🚨 Problematic attributes found:")
        for prob in problematic_modules:
            print(f"  - {prob}")
    else:
        print("✅ No LazyString issues found in modules")
    
    return len(problematic_modules) == 0

def provide_recommendations():
    """Provide specific recommendations based on findings"""
    print("\n💡 Recommendations:")
    print("1. Run: pip install flask-babel")
    print("2. Use the Emergency LazyString Fix:")
    print("   python3 emergency_lazystring_fix.py")
    print("3. If that fails, use the Comprehensive Fix:")
    print("   python3 comprehensive_lazystring_fix.py")
    print("4. Check that WTF_CSRF_ENABLED=False in environment")

def main():
    """Run complete diagnostic"""
    print("🔍 LazyString Error Diagnostic")
    print("=" * 35)
    
    # Setup
    setup_minimal_env()
    
    # Run tests
    tests = [
        ("JSON Baseline", test_json_baseline),
        ("Flask-Babel LazyString", test_flask_babel_lazystring),
        ("Specific Modules", test_specific_modules),
        ("App Creation", test_app_creation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n📊 Diagnostic Summary")
    print("=" * 25)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    failed_tests = [name for name, passed in results.items() if not passed]
    
    if failed_tests:
        print(f"\n🚨 Failed tests: {', '.join(failed_tests)}")
        if "Flask-Babel LazyString" in failed_tests:
            print("💡 LazyString serialization is definitely the issue")
        if "App Creation" in failed_tests:
            print("💡 LazyString errors occur during app creation")
    else:
        print("\n🎉 All tests passed! LazyString might not be the issue.")
    
    provide_recommendations()

if __name__ == "__main__":
    main()