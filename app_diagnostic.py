#!/usr/bin/env python3
"""
Application Diagnostic Script
Diagnoses issues with Dash/Flask app setup and LazyString problems

Run this before using the launchers to identify potential issues.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AppDiagnostic:
    """Comprehensive app diagnostic tool"""
    
    def __init__(self):
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
        
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic suite"""
        print("🔍 Application Diagnostic Suite")
        print("=" * 50)
        
        results = {}
        
        # 1. Environment check
        results['environment'] = self._check_environment()
        
        # 2. Dependencies check
        results['dependencies'] = self._check_dependencies()
        
        # 3. Configuration check
        results['configuration'] = self._check_configuration()
        
        # 4. App structure check
        results['app_structure'] = self._check_app_structure()
        
        # 5. LazyString check
        results['lazystring'] = self._check_lazystring_issues()
        
        # 6. App creation test
        results['app_creation'] = self._test_app_creation()
        
        # Generate report
        self._generate_report(results)
        
        return results
    
    def _check_environment(self) -> Dict[str, Any]:
        """Check environment variables and setup"""
        print("\n📋 Checking Environment...")
        
        env_result = {
            'python_version': sys.version,
            'current_directory': str(Path.cwd()),
            'environment_variables': {},
            'missing_env_vars': []
        }
        
        # Check important environment variables
        important_vars = [
            'FLASK_ENV', 'FLASK_DEBUG', 'SECRET_KEY', 
            'YOSAI_ENV', 'YOSAI_CONFIG_FILE', 'DB_HOST'
        ]
        
        for var in important_vars:
            value = os.getenv(var)
            if value:
                env_result['environment_variables'][var] = value
            else:
                env_result['missing_env_vars'].append(var)
        
        # Check for .env file
        env_file = Path('.env')
        env_result['env_file_exists'] = env_file.exists()
        
        if not env_file.exists():
            self.warnings.append("No .env file found - using system environment only")
        
        print(f"✅ Python version: {sys.version.split()[0]}")
        print(f"✅ Working directory: {Path.cwd()}")
        print(f"✅ Environment variables set: {len(env_result['environment_variables'])}")
        
        if env_result['missing_env_vars']:
            print(f"⚠️ Missing env vars: {', '.join(env_result['missing_env_vars'])}")
        
        return env_result
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check required dependencies"""
        print("\n📦 Checking Dependencies...")
        
        deps_result = {
            'installed': {},
            'missing': [],
            'version_conflicts': []
        }
        
        # Check core dependencies
        required_packages = {
            'dash': '2.14.0',
            'flask': '2.0.0',
            'flask-babel': '2.0.0',
            'plotly': '5.0.0',
            'pandas': '1.0.0'
        }
        
        for package, min_version in required_packages.items():
            try:
                imported = __import__(package)
                version = getattr(imported, '__version__', 'unknown')
                deps_result['installed'][package] = version
                print(f"✅ {package}: {version}")
            except ImportError:
                deps_result['missing'].append(package)
                print(f"❌ {package}: Not installed")
                self.issues.append(f"Missing dependency: {package}")
        
        return deps_result
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration files"""
        print("\n⚙️ Checking Configuration...")
        
        config_result = {
            'config_files': {},
            'config_accessible': False
        }
        
        # Check for configuration files
        config_files = [
            'config/config.yaml',
            'config/production.yaml',
            'config/test.yaml'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            exists = config_path.exists()
            config_result['config_files'][config_file] = exists
            
            status = "✅" if exists else "❌"
            print(f"{status} {config_file}: {'Found' if exists else 'Not found'}")
            
            if not exists and 'config.yaml' in config_file:
                self.issues.append(f"Main config file missing: {config_file}")
        
        # Try to load configuration manager
        try:
            from config.yaml_config import ConfigurationManager
            config_manager = ConfigurationManager()
            config_result['config_accessible'] = True
            print("✅ Configuration manager accessible")
        except ImportError as e:
            config_result['config_accessible'] = False
            print(f"❌ Configuration manager not accessible: {e}")
            self.issues.append("Cannot import ConfigurationManager")
        
        return config_result
    
    def _check_app_structure(self) -> Dict[str, Any]:
        """Check app structure and imports"""
        print("\n🏗️ Checking App Structure...")
        
        structure_result = {
            'core_modules': {},
            'app_factory_accessible': False,
            'panels_accessible': {}
        }
        
        # Check core modules
        core_modules = [
            'core.app_factory',
            'core.secret_manager',
            'config.yaml_config'
        ]
        
        for module in core_modules:
            try:
                __import__(module)
                structure_result['core_modules'][module] = True
                print(f"✅ {module}: Accessible")
            except ImportError as e:
                structure_result['core_modules'][module] = False
                print(f"❌ {module}: {e}")
                self.issues.append(f"Cannot import {module}")
        
        # Check app factory specifically
        try:
            from core.app_factory import create_application
            structure_result['app_factory_accessible'] = True
            print("✅ App factory: create_application function found")
        except ImportError:
            structure_result['app_factory_accessible'] = False
            print("❌ App factory: create_application function not accessible")
            self.issues.append("Cannot import create_application function")
        
        # Check panel modules
        panel_modules = [
            'components.map_panel',
            'components.bottom_panel', 
            'components.incident_alerts_panel',
            'components.weak_signal_panel'
        ]
        
        for module in panel_modules:
            try:
                __import__(module)
                structure_result['panels_accessible'][module] = True
                print(f"✅ Panel {module}: Accessible")
            except ImportError:
                structure_result['panels_accessible'][module] = False
                print(f"⚠️ Panel {module}: Not accessible (may be optional)")
                self.warnings.append(f"Panel not accessible: {module}")
        
        return structure_result
    
    def _check_lazystring_issues(self) -> Dict[str, Any]:
        """Check for LazyString serialization issues"""
        print("\n🔤 Checking LazyString Issues...")
        
        lazystring_result = {
            'babel_available': False,
            'lazystring_detected': False,
            'serialization_breaks': False,
            'plugin_available': False
        }
        
        # Check Flask-Babel
        try:
            from flask_babel import lazy_gettext as _l
            lazystring_result['babel_available'] = True
            print("✅ Flask-Babel: Available")
            
            # Test LazyString creation
            lazy_str = _l("Test string")
            is_lazystring = 'LazyString' in str(type(lazy_str))
            lazystring_result['lazystring_detected'] = is_lazystring
            
            if is_lazystring:
                print(f"✅ LazyString detected: {type(lazy_str)}")
                
                # Test serialization
                try:
                    json.dumps({"test": lazy_str})
                    print("⚠️ LazyString serialized unexpectedly (may already be fixed)")
                    lazystring_result['serialization_breaks'] = False
                except TypeError:
                    print("❌ LazyString breaks JSON serialization (needs fixing)")
                    lazystring_result['serialization_breaks'] = True
                    self.issues.append("LazyString breaks JSON serialization")
            else:
                print("⚠️ LazyString not detected (may already be patched)")
                
        except ImportError:
            print("⚠️ Flask-Babel: Not available")
            lazystring_result['babel_available'] = False
        
        # Check if plugin is available
        try:
            from lazystring_plugin import LazyStringSerializationPlugin
            lazystring_result['plugin_available'] = True
            print("✅ LazyString plugin: Available")
        except ImportError:
            lazystring_result['plugin_available'] = False
            print("❌ LazyString plugin: Not available")
            self.suggestions.append("Download and save the LazyString plugin as lazystring_plugin.py")
        
        return lazystring_result
    
    def _test_app_creation(self) -> Dict[str, Any]:
        """Test app creation without running"""
        print("\n🧪 Testing App Creation...")
        
        app_test_result = {
            'app_created': False,
            'app_type': None,
            'has_run_method': False,
            'has_run_server_method': False,
            'error_message': None
        }
        
        try:
            # Set up minimal environment
            os.environ.setdefault('SECRET_KEY', 'test-key')
            os.environ.setdefault('YOSAI_ENV', 'development')
            os.environ.setdefault('WTF_CSRF_ENABLED', 'False')
            
            from core.app_factory import create_application
            app = create_application()
            
            if app is not None:
                app_test_result['app_created'] = True
                app_test_result['app_type'] = type(app).__name__
                app_test_result['has_run_method'] = hasattr(app, 'run')
                app_test_result['has_run_server_method'] = hasattr(app, 'run_server')
                
                print(f"✅ App created successfully: {type(app).__name__}")
                print(f"✅ Has run method: {app_test_result['has_run_method']}")
                print(f"✅ Has run_server method: {app_test_result['has_run_server_method']}")
                
                # Test callback detection
                if hasattr(app, 'callback_map'):
                    callback_count = len(app.callback_map) if app.callback_map else 0
                    print(f"✅ Dash callbacks detected: {callback_count}")
                
            else:
                print("❌ App creation returned None")
                app_test_result['error_message'] = "create_application returned None"
                self.issues.append("App factory returned None")
                
        except Exception as e:
            print(f"❌ App creation failed: {e}")
            app_test_result['error_message'] = str(e)
            self.issues.append(f"App creation error: {e}")
        
        return app_test_result
    
    def _generate_report(self, results: Dict[str, Any]) -> None:
        """Generate diagnostic report"""
        print(f"\n📊 Diagnostic Report")
        print("=" * 30)
        
        # Count issues
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        if total_issues == 0:
            print("🎉 No critical issues found!")
        else:
            print(f"🚨 Found {total_issues} critical issues:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if total_warnings > 0:
            print(f"\n⚠️ Found {total_warnings} warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if not results['dependencies']['missing']:
            print("✅ All dependencies are installed")
        else:
            print("1. Install missing dependencies:")
            for dep in results['dependencies']['missing']:
                print(f"   pip install {dep}")
        
        if not results['configuration']['config_accessible']:
            print("2. Check your configuration setup")
            print("   - Ensure config/config.yaml exists")
            print("   - Verify ConfigurationManager is accessible")
        
        if results['lazystring']['serialization_breaks']:
            print("3. Apply LazyString fixes:")
            print("   - Save lazystring_plugin.py in your project")
            print("   - Use: python3 app_launcher.py --mode protected")
        
        if not results['app_structure']['app_factory_accessible']:
            print("4. Fix app factory issues:")
            print("   - Check core.app_factory module")
            print("   - Ensure create_application function exists")
        
        # Custom suggestions
        for suggestion in self.suggestions:
            print(f"   • {suggestion}")
        
        # Next steps
        print(f"\n🚀 Next Steps:")
        if total_issues == 0:
            print("1. Try: python3 app_launcher.py --mode protected")
            print("2. If LazyString errors occur, run the protected mode")
            print("3. Test with: python3 lazystring_test_suite.py")
        else:
            print("1. Fix the critical issues listed above")
            print("2. Re-run this diagnostic: python3 app_diagnostic.py")
            print("3. Once issues are resolved, use the protected launcher")


def main():
    """Main diagnostic entry point"""
    diagnostic = AppDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # Return exit code based on issues found
    return 1 if diagnostic.issues else 0


if __name__ == "__main__":
    sys.exit(main())