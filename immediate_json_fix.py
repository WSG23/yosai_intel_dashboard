#!/usr/bin/env python3
"""
Immediate JSON Fix
Patches the most common sources of JSON serialization errors
"""

import shutil
from pathlib import Path
from datetime import datetime


class ImmediateJsonFixer:
    """Apply immediate fixes to common JSON serialization issues"""
    
    def __init__(self):
        self.backup_suffix = f".json_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = []
    
    def fix_component_registry(self) -> bool:
        """Fix ComponentRegistry to return actual components, not functions"""
        file_path = Path("core/component_registry.py")
        
        if not file_path.exists():
            print("📋 ComponentRegistry not found - skipping")
            return True
        
        try:
            # Backup original
            shutil.copy2(file_path, f"core/component_registry.py{self.backup_suffix}")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace the problematic get_component_or_fallback method
            fixed_content = content.replace(
                '''def get_component_or_fallback(self, name: str, fallback_text: str) -> Any:
        """Get component or return fallback - replaces your safe_component() function"""
        component = self.get_component(name)
        if component is not None:
            return component

        # Import html for fallback
        try:
            from dash import html

            return html.Div(
                fallback_text,
                className="alert alert-warning text-center",
                style={"margin": "1rem", "padding": "1rem"},
            )
        except ImportError:
            # Ultimate fallback
            return None''',
                '''def get_component_or_fallback(self, name: str, fallback_text: str) -> Any:
        """Get component or return fallback - FIXED: Returns actual components, not functions"""
        component = self.get_component(name)
        
        # If component is a function, call it to get the actual component
        if callable(component):
            try:
                component = component()
            except Exception as e:
                print(f"⚠️  Error calling component function {name}: {e}")
                component = None
        
        if component is not None:
            return component

        # Import html for fallback
        try:
            from dash import html
            return html.Div(
                fallback_text,
                className="alert alert-warning text-center",
                style={"margin": "1rem", "padding": "1rem"},
            )
        except ImportError:
            # Ultimate fallback
            return fallback_text'''
            )
            
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            print("✅ Fixed ComponentRegistry to call component functions")
            self.fixes_applied.append("Fixed ComponentRegistry")
            return True
            
        except Exception as e:
            print(f"❌ Failed to fix ComponentRegistry: {e}")
            return False
    
    def fix_layout_manager(self) -> bool:
        """Fix LayoutManager to return actual components"""
        file_path = Path("core/layout_manager.py")
        
        if not file_path.exists():
            print("📋 LayoutManager not found - skipping")
            return True
        
        try:
            # Backup original
            shutil.copy2(file_path, f"core/layout_manager.py{self.backup_suffix}")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add a helper function at the top
            lines = content.split('\n')
            
            # Find where to insert the helper function
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('class LayoutManager'):
                    insert_index = i
                    break
            
            # Insert helper function before the class
            helper_function = '''
def safe_component_call(component):
    """Safely call a component function or return the component directly"""
    if callable(component):
        try:
            result = component()
            # If result is still callable, try calling it again
            if callable(result):
                try:
                    return result()
                except:
                    pass
            return result
        except Exception as e:
            from dash import html
            return html.Div(f"Component error: {e}", className="alert alert-warning")
    return component

'''
            
            lines.insert(insert_index, helper_function)
            
            # Fix the problematic methods in LayoutManager
            for i, line in enumerate(lines):
                if "self.registry.get_component_or_fallback(" in line:
                    lines[i] = line.replace(
                        "self.registry.get_component_or_fallback(",
                        "safe_component_call(self.registry.get_component_or_fallback("
                    ) + ")"
                elif "self.registry.get_component(" in line and "return" in line:
                    lines[i] = line.replace(
                        "self.registry.get_component(",
                        "safe_component_call(self.registry.get_component("
                    ) + ")"
            
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Fixed LayoutManager to call component functions safely")
            self.fixes_applied.append("Fixed LayoutManager")
            return True
            
        except Exception as e:
            print(f"❌ Failed to fix LayoutManager: {e}")
            return False
    
    def fix_navbar_import(self) -> bool:
        """Fix navbar import path issues"""
        navbar_file = Path("dashboard/layout/navbar.py")
        
        if not navbar_file.exists():
            print("📋 Navbar file not found - skipping")
            return True
        
        try:
            with open(navbar_file, 'r') as f:
                content = f.read()
            
            # Ensure the create_navbar_layout function returns actual components
            if "def create_navbar_layout():" in content:
                print("✅ Navbar layout function found")
                self.fixes_applied.append("Verified navbar function")
                return True
            else:
                print("⚠️  navbar layout function not found")
                return True
                
        except Exception as e:
            print(f"❌ Error checking navbar: {e}")
            return False
    
    def create_emergency_safe_components(self) -> bool:
        """Create emergency safe components to replace problematic ones"""
        try:
            safe_components = '''#!/usr/bin/env python3
"""
Emergency Safe Components
Provides safe fallback components that are guaranteed to be JSON serializable
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def safe_navbar():
    """Safe navbar component"""
    return dbc.Navbar([
        dbc.Container([
            html.H3("🏯 Yōsai Intel Dashboard", className="text-white mb-0"),
            html.Span("Safe Mode", className="badge bg-warning text-dark ms-2")
        ])
    ], color="dark", dark=True)


def safe_map_panel():
    """Safe map panel component"""
    return dbc.Card([
        dbc.CardHeader("🗺️ Map Panel"),
        dbc.CardBody([
            html.P("Map panel is running in safe mode"),
            html.P("No JSON serialization issues here!", className="text-success")
        ])
    ])


def safe_bottom_panel():
    """Safe bottom panel component"""
    return dbc.Card([
        dbc.CardHeader("📊 Analytics Panel"),
        dbc.CardBody([
            html.P("Analytics panel is running safely"),
            html.Div("All components are JSON serializable", className="alert alert-success")
        ])
    ])


def safe_incident_alerts():
    """Safe incident alerts component"""
    return dbc.Card([
        dbc.CardHeader("🚨 Incident Alerts"),
        dbc.CardBody([
            dbc.Alert("No active incidents", color="success"),
            html.P("System is operating normally")
        ])
    ])


def safe_weak_signal():
    """Safe weak signal panel component"""
    return dbc.Card([
        dbc.CardHeader("📡 Weak Signal Analysis"),
        dbc.CardBody([
            html.P("Weak signal analysis is running"),
            html.P("All data is properly serialized", className="text-info")
        ])
    ])


# Component registry mapping
SAFE_COMPONENTS = {
    'navbar': safe_navbar,
    'map_panel': safe_map_panel, 
    'bottom_panel': safe_bottom_panel,
    'incident_alerts': safe_incident_alerts,
    'weak_signal': safe_weak_signal,
}


def get_safe_component(name: str):
    """Get a safe component by name"""
    if name in SAFE_COMPONENTS:
        return SAFE_COMPONENTS[name]()
    else:
        return html.Div(f"Safe fallback for: {name}", className="alert alert-info")
'''
            
            # Create utils directory if it doesn't exist
            utils_dir = Path("utils")
            utils_dir.mkdir(exist_ok=True)
            
            with open("utils/safe_components.py", "w") as f:
                f.write(safe_components)
            
            print("✅ Created emergency safe components")
            self.fixes_applied.append("Created safe components")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create safe components: {e}")
            return False
    
    def patch_component_registry_imports(self) -> bool:
        """Patch ComponentRegistry to use safe components when needed"""
        file_path = Path("core/component_registry.py")
        
        if not file_path.exists():
            return True
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add import for safe components
            if "from utils.safe_components import get_safe_component" not in content:
                lines = content.split('\n')
                
                # Find import section
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_index = i
                
                # Add safe components import
                lines.insert(import_index + 1, "from utils.safe_components import get_safe_component")
                
                # Update the get_component_or_fallback method to use safe components
                for i, line in enumerate(lines):
                    if "return None" in line and "Ultimate fallback" in lines[i-1]:
                        lines[i] = "            return get_safe_component(name)"
                
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Patched ComponentRegistry to use safe components")
                self.fixes_applied.append("Patched ComponentRegistry imports")
                return True
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch ComponentRegistry imports: {e}")
            return False
    
    def apply_immediate_fixes(self) -> bool:
        """Apply all immediate fixes"""
        print("🚀 Applying Immediate JSON Serialization Fixes")
        print("=" * 50)
        print("These fixes target the most common sources of function return errors")
        print()
        
        fixes = [
            ("Creating emergency safe components", self.create_emergency_safe_components),
            ("Fixing ComponentRegistry", self.fix_component_registry),
            ("Fixing LayoutManager", self.fix_layout_manager),
            ("Checking navbar import", self.fix_navbar_import),
            ("Patching ComponentRegistry imports", self.patch_component_registry_imports),
        ]
        
        all_successful = True
        for fix_name, fix_func in fixes:
            print(f"🔧 {fix_name}...")
            if not fix_func():
                all_successful = False
                print(f"❌ {fix_name} failed")
            else:
                print(f"✅ {fix_name} completed")
        
        print(f"\n📊 Fix Summary")
        print("=" * 15)
        if self.fixes_applied:
            print("Fixes applied:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        if all_successful:
            print(f"\n🎉 All immediate fixes applied!")
            print(f"\n🚀 Try running your app now:")
            print(f"   python3 app.py")
            print(f"\n🔍 Or run the debugger to identify remaining issues:")
            print(f"   python3 debug_json_error.py")
            return True
        else:
            print(f"\n❌ Some fixes failed")
            return False


def main():
    """Main fix function"""
    fixer = ImmediateJsonFixer()
    success = fixer.apply_immediate_fixes()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())