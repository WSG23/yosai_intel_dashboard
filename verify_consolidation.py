#!/usr/bin/env python3
"""
Verify Complete Consolidation
"""
import sys


def verify_imports():
    """Test all critical imports"""
    try:
        from services.analytics_service import get_analytics_service
        from models.base import ModelFactory
        from pages.file_upload import get_uploaded_data
        from config.config import get_config
        print("✅ All critical imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def verify_analytics_service():
    """Test analytics service"""
    try:
        service = get_analytics_service()
        health = service.health_check()
        analytics = service.get_analytics_by_source("sample")
        print("✅ Analytics service working")
        return True
    except Exception as e:
        print(f"❌ Analytics service error: {e}")
        return False


def verify_models():
    """Test model system"""
    try:
        import pandas as pd
        df = pd.DataFrame({'test': [1, 2, 3]})
        models = ModelFactory.create_models_from_dataframe(df)
        print("✅ Model system working")
        return True
    except Exception as e:
        print(f"❌ Model system error: {e}")
        return False


def main():
    print("🔧 CONSOLIDATION VERIFICATION")
    print("=" * 40)

    tests = [
        ("Import Test", verify_imports),
        ("Analytics Service", verify_analytics_service),
        ("Model System", verify_models)
    ]

    passed = 0
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        if test_func():
            passed += 1

    print(f"\n📊 RESULT: {passed}/{len(tests)} tests passed")
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
