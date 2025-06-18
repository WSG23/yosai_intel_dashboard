#!/usr/bin/env python3
"""
Modular Dependency Manager
Checks, validates, and manages Python dependencies for the Yosai Intel Dashboard
"""

import subprocess
import sys
import importlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DependencyInfo:
    """Information about a single dependency"""
    name: str
    required_version: str
    installed_version: Optional[str] = None
    is_installed: bool = False
    import_name: Optional[str] = None


class DependencyChecker:
    """Modular dependency checker and validator"""
    
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.dependencies: List[DependencyInfo] = []
        
    def parse_requirements(self) -> List[DependencyInfo]:
        """Parse requirements.txt file and extract dependency information"""
        if not self.requirements_file.exists():
            raise FileNotFoundError(f"Requirements file not found: {self.requirements_file}")
            
        dependencies = []
        
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                    
                # Parse package name and version
                if '>=' in line:
                    name, version = line.split('>=')
                elif '==' in line:
                    name, version = line.split('==')
                elif '>' in line:
                    name, version = line.split('>')
                else:
                    name, version = line, "*"
                    
                # Clean up the strings
                name = name.strip()
                version = version.strip()
                
                # Handle special import names
                import_name = self._get_import_name(name)
                
                dep = DependencyInfo(
                    name=name, 
                    required_version=version,
                    import_name=import_name
                )
                dependencies.append(dep)
                
        self.dependencies = dependencies
        return dependencies
    
    def _get_import_name(self, package_name: str) -> str:
        """Get the actual import name for a package (some differ from pip name)"""
        import_mapping = {
            'flask-login': 'flask_login',
            'dash-bootstrap-components': 'dash_bootstrap_components',
            'python-dotenv': 'dotenv',
            'python-multipart': 'multipart',
            'psycopg2-binary': 'psycopg2',
            'python-jose': 'jose',
            'Flask-Babel': 'flask_babel',
            'flask-wtf': 'flask_wtf',
            'dash-leaflet': 'dash_leaflet',
        }
        return import_mapping.get(package_name, package_name.replace('-', '_'))
    
    def check_installed_packages(self) -> Dict[str, str]:
        """Get list of currently installed packages"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
                capture_output=True,
                text=True,
                check=True
            )
            
            installed = {}
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    name, version = line.split('==')
                    installed[name.lower()] = version
                    
            return installed
        except subprocess.CalledProcessError as e:
            print(f"Error checking installed packages: {e}")
            return {}
    
    def validate_dependencies(self) -> Tuple[List[DependencyInfo], List[DependencyInfo]]:
        """Validate all dependencies and return missing/installed lists"""
        installed_packages = self.check_installed_packages()
        
        missing = []
        satisfied = []
        
        for dep in self.dependencies:
            package_key = dep.name.lower()
            
            if package_key in installed_packages:
                dep.installed_version = installed_packages[package_key]
                dep.is_installed = True
                
                # Try to import the package to verify it works
                try:
                    importlib.import_module(dep.import_name)
                    satisfied.append(dep)
                except ImportError:
                    print(f"⚠️  {dep.name} is installed but cannot be imported as '{dep.import_name}'")
                    missing.append(dep)
            else:
                missing.append(dep)
                
        return missing, satisfied
    
    def install_missing_dependencies(self, missing_deps: List[DependencyInfo]) -> bool:
        """Install missing dependencies"""
        if not missing_deps:
            print("✅ All dependencies are already installed!")
            return True
            
        print(f"📦 Installing {len(missing_deps)} missing dependencies...")
        
        for dep in missing_deps:
            print(f"   Installing {dep.name}>={dep.required_version}...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', f"{dep.name}>={dep.required_version}"],
                    check=True,
                    capture_output=True
                )
                print(f"   ✅ {dep.name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {dep.name}: {e}")
                return False
                
        return True
    
    def generate_report(self) -> str:
        """Generate a dependency status report"""
        missing, satisfied = self.validate_dependencies()
        
        report = []
        report.append("=" * 60)
        report.append("DEPENDENCY STATUS REPORT")
        report.append("=" * 60)
        report.append(f"Total dependencies: {len(self.dependencies)}")
        report.append(f"✅ Satisfied: {len(satisfied)}")
        report.append(f"❌ Missing: {len(missing)}")
        report.append("")
        
        if satisfied:
            report.append("SATISFIED DEPENDENCIES:")
            report.append("-" * 40)
            for dep in satisfied:
                report.append(f"✅ {dep.name} {dep.installed_version} (required: >={dep.required_version})")
            report.append("")
        
        if missing:
            report.append("MISSING DEPENDENCIES:")
            report.append("-" * 40)
            for dep in missing:
                report.append(f"❌ {dep.name} (required: >={dep.required_version})")
            report.append("")
            
        return "\n".join(report)


class DependencyManager:
    """Main dependency management interface"""
    
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.checker = DependencyChecker(requirements_file)
        
    def check_and_install(self) -> bool:
        """Check dependencies and install missing ones"""
        print("🔍 Parsing requirements...")
        self.checker.parse_requirements()
        
        print("🔍 Checking installed packages...")
        missing, satisfied = self.checker.validate_dependencies()
        
        print(self.checker.generate_report())
        
        if missing:
            response = input("Install missing dependencies? [Y/n]: ").strip().lower()
            if response in ['', 'y', 'yes']:
                return self.checker.install_missing_dependencies(missing)
            else:
                print("Skipping installation.")
                return False
        
        return True
    
    def verify_critical_imports(self) -> bool:
        """Verify that critical imports work"""
        critical_imports = [
            'flask_login',
            'dash',
            'flask',
            'authlib',
            'jose'
        ]
        
        print("🔍 Verifying critical imports...")
        all_good = True
        
        for import_name in critical_imports:
            try:
                importlib.import_module(import_name)
                print(f"✅ {import_name}")
            except ImportError as e:
                print(f"❌ {import_name}: {e}")
                all_good = False
                
        return all_good


def main():
    """Main entry point for dependency management"""
    manager = DependencyManager()
    
    print("🚀 Yosai Intel Dashboard - Dependency Manager")
    print("=" * 50)
    
    # Check and install dependencies
    if manager.check_and_install():
        print("\n🔍 Verifying critical imports...")
        if manager.verify_critical_imports():
            print("\n✅ All dependencies are working correctly!")
            print("🚀 You can now run: python3 app.py")
        else:
            print("\n❌ Some critical imports failed. Please check the errors above.")
            return 1
    else:
        print("\n❌ Dependency installation failed.")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())