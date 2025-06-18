#!/usr/bin/env python3
"""
Import Tester - Modular testing for specific import issues
Tests the exact imports that are failing in your application
"""

import sys
import importlib
from typing import List, Tuple


class ImportTester:
    """Modular class to test specific imports and diagnose issues"""
    
    def __init__(self):
        self.results = []
    
    def test_import(self, module_name: str, description: str = "") -> bool:
        """Test a single import and return success status"""
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {module_name} (v{version}) - {description}")
            self.results.append((module_name, True, version, description))
            return True
        except ImportError as e:
            print(f"❌ {module_name} - FAILED: {e}")
            self.results.append((module_name, False, str(e), description))
            return False
        except Exception as e:
            print(f"⚠️  {module_name} - WARNING: {e}")
            self.results.append((module_name, False, str(e), description))
            return False
    
    def test_your_app_imports(self) -> bool:
        """Test the specific imports your app needs"""
        print("🔍 Testing Yosai Intel Dashboard Critical Imports")
        print("=" * 55)
        
        imports_to_test = [
            ('flask_login', 'Flask-Login authentication'),
            ('flask', 'Flask web framework'),
            ('dash', 'Dash framework'),
            ('authlib', 'OAuth/OIDC authentication'),
            ('jose', 'JWT token processing'),
            ('flask_wtf', 'Flask WTF forms'),
            ('flask_babel', 'Flask internationalization'),
            ('dash_bootstrap_components', 'Bootstrap components for Dash'),
            ('plotly', 'Plotly visualization'),
            ('pandas', 'Data processing'),
            ('psycopg2', 'PostgreSQL adapter'),
            ('sqlalchemy', 'SQL toolkit'),
        ]
        
        all_passed = True
        for module_name, description in imports_to_test:
            if not self.test_import(module_name, description):
                all_passed = False
        
        return all_passed
    
    def test_specific_flask_login_imports(self) -> bool:
        """Test the specific flask_login imports your code uses"""
        print("\n🔍 Testing Specific Flask-Login Imports")
        print("=" * 40)
        
        flask_login_imports = [
            'flask_login.LoginManager',
            'flask_login.UserMixin', 
            'flask_login.login_required',
            'flask_login.login_user',
            'flask_login.logout_user',
            'flask_login.current_user',
        ]
        
        all_passed = True
        for import_path in flask_login_imports:
            module_name, class_name = import_path.rsplit('.', 1)
            try:
                module = importlib.import_module(module_name)
                getattr(module, class_name)
                print(f"✅ {import_path}")
            except (ImportError, AttributeError) as e:
                print(f"❌ {import_path} - FAILED: {e}")
                all_passed = False
        
        return all_passed
    
    def diagnose_environment(self):
        """Diagnose the Python environment"""
        print("\n🔍 Environment Diagnosis")
        print("=" * 25)
        print(f"Python executable: {sys.executable}")
        print(f"Python version: {sys.version}")
        
        # Check if in virtual environment
        virtual_env = sys.prefix != sys.base_prefix
        print(f"Virtual environment: {'Yes' if virtual_env else 'No'}")
        
        if virtual_env:
            print(f"Virtual env path: {sys.prefix}")
        
        # Check pip version
        try:
            import pip
            print(f"Pip version: {pip.__version__}")
        except ImportError:
            print("Pip: Not available as module")
    
    def suggest_fixes(self):
        """Suggest fixes based on test results"""
        print("\n🔧 Suggested Fixes")
        print("=" * 20)
        
        failed_imports = [result for result in self.results if not result[1]]
        
        if not failed_imports:
            print("✅ No fixes needed - all imports working!")
            return
        
        print("Run these commands to fix missing dependencies:")
        print()
        
        # Upgrade pip first
        print("1. Upgrade pip:")
        print("   python3 -m pip install --upgrade pip")
        print()
        
        # Install requirements
        print("2. Install requirements:")
        print("   python3 -m pip install -r requirements.txt")
        print()
        
        # Install specific failed packages
        package_mapping = {
            'flask_login': 'flask-login',
            'dash_bootstrap_components': 'dash-bootstrap-components',
            'flask_wtf': 'flask-wtf',
            'flask_babel': 'Flask-Babel',
            'jose': 'python-jose',
        }
        
        print("3. Or install specific packages:")
        for module_name, success, error, desc in failed_imports:
            package_name = package_mapping.get(module_name, module_name)
            print(f"   python3 -m pip install {package_name}")
        
        print()
        print("4. If using a virtual environment, make sure it's activated:")
        print("   source venv/bin/activate  # macOS/Linux")
        print("   venv\\Scripts\\activate     # Windows")


def main():
    """Main testing function"""
    tester = ImportTester()
    
    print("🚀 Yosai Intel Dashboard - Import Tester")
    print("=" * 45)
    
    # Test environment
    tester.diagnose_environment()
    
    # Test main imports
    main_imports_ok = tester.test_your_app_imports()
    
    # Test specific flask_login imports if main test passed
    if main_imports_ok:
        flask_login_ok = tester.test_specific_flask_login_imports()
        
        if flask_login_ok:
            print("\n✅ ALL TESTS PASSED!")
            print("🚀 Your app should run without import errors.")
            return 0
    
    # Suggest fixes if any tests failed
    tester.suggest_fixes()
    
    print("\n❌ Some imports failed. Follow the suggested fixes above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())