#!/usr/bin/env python3
"""Test the modular configuration system"""

import sys
import types

# Provide dummy dash module if not installed
if 'dash' not in sys.modules:
    sys.modules['dash'] = types.ModuleType('dash')
if 'flask_login' not in sys.modules:
    mod = types.ModuleType('flask_login')
    def login_required(func):
        return func
    mod.login_required = login_required
    sys.modules['flask_login'] = mod
if 'flask_wtf' not in sys.modules:
    fw = types.ModuleType('flask_wtf')
    class CSRFProtect:
        def __init__(self, app=None):
            pass
    fw.CSRFProtect = CSRFProtect
    sys.modules['flask_wtf'] = fw
if 'flask' not in sys.modules:
    fl = types.ModuleType('flask')
    fl.session = {}
    def redirect(x, *a, **k):
        return x
    fl.redirect = redirect
    class Blueprint:
        def __init__(self, *a, **k):
            pass
    fl.Blueprint = Blueprint
    fl.request = types.SimpleNamespace()
    sys.modules['flask'] = fl
if 'flask_babel' not in sys.modules:
    fb = types.ModuleType('flask_babel')
    class Babel:
        def __init__(self, app=None):
            pass
        def init_app(self, app):
            pass
    def lazy_gettext(text):
        return text
    fb.Babel = Babel
    fb.lazy_gettext = lazy_gettext
    sys.modules['flask_babel'] = fb

def test_imports():
    """Test that all modules can be imported"""
    try:
        from core.plugins.config import (
            IDatabaseManager,
            ICacheManager,
            IConfigurationManager,
            DatabaseManagerFactory,
            CacheManagerFactory,
            get_service_locator,
            get_config
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    try:
        from core.plugins.config import get_config
        config_manager = get_config()
        config_manager.load_configuration(None)  # Use defaults
        print(f"✅ Configuration loaded - Database: {config_manager.database_config.type}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_service_locator():
    """Test service locator"""
    try:
        from core.plugins.config import get_config, get_service_locator
        config_manager = get_config()
        config_manager.load_configuration(None)
        service_locator = get_service_locator()
        service_locator.initialize_from_config(config_manager)
        service_locator.start_services()
        # Test services
        db_manager = service_locator.get_database_manager()
        cache_manager = service_locator.get_cache_manager()
        if db_manager and cache_manager:
            print("✅ Service locator working")
            return True
        else:
            print("❌ Service locator failed to create services")
            return False
    except Exception as e:
        print(f"❌ Service locator test failed: {e}")
        return False

def test_database_factory():
    """Test database factory"""
    try:
        from core.plugins.config import DatabaseManagerFactory, get_config
        config_manager = get_config()
        config_manager.load_configuration(None)
        db_manager = DatabaseManagerFactory.create_manager(config_manager.database_config)
        result = db_manager.get_connection()
        if result.success:
            print(f"✅ Database factory working - Created {result.connection_type} manager")
            return True
        else:
            print("❌ Database factory failed")
            return False
    except Exception as e:
        print(f"❌ Database factory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Modular Configuration System")
    print("=" * 50)
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Service Locator Test", test_service_locator),
        ("Database Factory Test", test_database_factory),
    ]
    passed = 0
    for name, test_func in tests:
        print(f"\n🔍 {name}:")
        if test_func():
            passed += 1
    print(f"\n" + "=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("🎉 All tests passed! Modular configuration system is working.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
