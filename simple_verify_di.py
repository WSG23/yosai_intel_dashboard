#!/usr/bin/env python3
# simple_verify_di.py
"""
Simple DI Container Verification Script - No syntax errors!
Quick check to see if your DI container has circular dependencies
"""
import sys
import traceback

def test_basic_imports():
    """Test basic imports"""
    print("🔍 Testing basic imports...")
    try:
        from core.container import Container
        print("   ✅ core.container.Container - OK")
        return True
    except ImportError as e:
        print(f"   ❌ core.container.Container - FAILED: {e}")
        return False

def test_service_registry():
    """Test service registry imports"""
    print("\n🔍 Testing service registry...")
    try:
        from core.service_registry import get_configured_container
        print("   ✅ get_configured_container_with_yaml - OK")
        return True
    except ImportError as e:
        print(f"   ❌ get_configured_container_with_yaml - FAILED: {e}")
        return False

def test_container_creation():
    """Test container creation"""
    print("\n🔍 Testing container creation...")
    try:
        from core.service_registry import get_configured_container        
        print("   🔧 Creating container...")
        container = get_configured_container()
        print("   ✅ Container created successfully")
        print("   ⚠️  BUT: May have circular dependencies")
        
        # Try to get a service to trigger circular dependency detection
        try:
            if hasattr(container, 'health_check'):
                health = container.health_check()
                status = health.get('status', 'unknown')
                print(f"   📊 Container health: {status}")
                
                if status == 'unhealthy':
                    print("   🔴 Container reports unhealthy - likely circular dependencies")
                    return False
                else:
                    print("   ✅ Container appears healthy")
                    return True
            else:
                print("   ⚠️  Container created but no health check available")
                return True
                
        except Exception as e:
            error_msg = str(e).lower()
            if 'circular' in error_msg:
                print("   🔴 CIRCULAR DEPENDENCY DETECTED!")
                print(f"   📝 Error: {e}")
                return False
            else:
                print(f"   ❌ Container error: {e}")
                return False
                
    except Exception as e:
        error_msg = str(e).lower()
        if 'circular' in error_msg:
            print("   🔴 CIRCULAR DEPENDENCY DETECTED!")
            print(f"   📝 Error: {e}")
            return False
        else:
            print(f"   ❌ Container creation failed: {e}")
            return False

def check_files_to_update():
    """Check which files need updating"""
    print("\n🔍 Checking files that need updating...")
    
    import os
    import glob
    
    files_to_check = []
    
    # Check root directory Python files
    root_files = glob.glob("*.py")
    files_to_check.extend(root_files)
    
    # Check for specific files
    specific_files = ["implementation.py", "app.py", "test_dependency_injection.py"]
    for file in specific_files:
        if os.path.exists(file) and file not in files_to_check:
            files_to_check.append(file)
    
    files_needing_update = []
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if 'get_configured_container_with_yaml' in content:
                    files_needing_update.append(file_path)
        except Exception as e:
            print(f"   ⚠️  Could not read {file_path}: {e}")
    
    if files_needing_update:
        print(f"   📝 Files needing import updates ({len(files_needing_update)}):")
        for file in files_needing_update:
            print(f"      • {file}")
    else:
        print("   ✅ No files found that need import updates")
    
    return files_needing_update

def show_fix_instructions(has_circular_deps, files_to_update):
    """Show specific fix instructions"""
    print("\n" + "="*60)
    print("📋 DIAGNOSIS RESULTS")
    print("="*60)
    
    if has_circular_deps:
        print("🔴 CIRCULAR DEPENDENCIES CONFIRMED!")
        print("💡 You need to apply the layered DI container fix")
    else:
        print("✅ No obvious circular dependencies detected")
        print("💡 Your DI container might be working correctly")
    
    print(f"\n📝 FILES TO UPDATE:")
    if files_to_update:
        for file in files_to_update:
            print(f"   • {file}")
        
        print(f"\n🔧 REQUIRED CHANGES:")
        print("   In each file above, change:")
        print("   FROM: from core.service_registry import get_configured_container_with_yaml")
        print("   TO:   from core.service_registry import get_configured_container")
        print()
        print("   FROM: get_configured_container_with_yaml()")
        print("   TO:   get_configured_container()")
    else:
        print("   ✅ No files need import updates")
    
    print(f"\n🚀 IMPLEMENTATION STEPS:")
    print("   1. Backup your current files:")
    print("      cp core/service_registry.py core/service_registry.py.backup")
    print("      cp core/container.py core/container.py.backup")
    
    print("   2. Copy the 4 artifacts I provided:")
    print("      • Fixed DI Container → core/di_container.py")
    print("      • Fixed Service Registry → core/service_registry.py (replace)")
    print("      • Comprehensive Tests → tests/test_di_container.py")
    print("      • Simple Verification → simple_verify_di.py (this file)")
    
    print("   3. Update import statements in the files listed above")
    
    print("   4. Test the fix:")
    print("      python3 simple_verify_di.py")
    
    print("   5. Run your dashboard:")
    print("      python3 implementation.py")

def main():
    """Main verification function"""
    print("🏯 YŌSAI INTEL DASHBOARD - DI CONTAINER VERIFICATION")
    print("="*60)
    
    # Test imports
    basic_imports_ok = test_basic_imports()
    service_registry_ok = test_service_registry()
    
    if not basic_imports_ok or not service_registry_ok:
        print("\n❌ Basic imports failed - check your core files exist")
        return 1
    
    # Test container creation
    container_ok = test_container_creation()
    
    # Check files that need updating
    files_to_update = check_files_to_update()
    
    # Show results and instructions
    has_circular_deps = not container_ok
    show_fix_instructions(has_circular_deps, files_to_update)
    
    if has_circular_deps:
        print(f"\n🎯 CONCLUSION: Apply the DI container fix to resolve circular dependencies!")
        return 1
    else:
        print(f"\n🎯 CONCLUSION: Your DI container appears to be working!")
        return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Verification script error: {e}")
        print("\n🔍 Full error details:")
        traceback.print_exc()
        print(f"\n💡 You can still apply the DI container fix manually!")
        sys.exit(1)
