#!/usr/bin/env python3
"""
Fix Layout Manager Syntax Error
Surgical fix for the malformed parentheses
"""

import shutil
from pathlib import Path
from datetime import datetime


def fix_layout_manager_syntax():
    """Fix the syntax error in layout_manager.py"""
    file_path = Path("core/layout_manager.py")
    
    if not file_path.exists():
        print("❌ layout_manager.py not found")
        return False
    
    try:
        # Backup first
        backup_file = f"core/layout_manager.py.syntax_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_file)
        print(f"✅ Backed up to {backup_file}")
        
        # Read current content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Show the problematic area
        lines = content.split('\n')
        print(f"\n🔍 Problem area around line 42:")
        for i in range(max(0, 40), min(len(lines), 45)):
            marker = "➤ " if i == 41 else "  "
            print(f"{marker}{i+1:2}: {lines[i]}")
        
        # Fix common syntax issues
        fixed_lines = []
        for i, line in enumerate(lines):
            # Fix unmatched parentheses
            if "safe_component_call(self.registry.get_component_or_fallback()" in line:
                # This line is malformed - fix it
                fixed_line = line.replace(
                    "safe_component_call(self.registry.get_component_or_fallback()",
                    "safe_component_call(self.registry.get_component_or_fallback("
                )
                
                # Find the arguments for get_component_or_fallback
                # Look for the next lines that might have the arguments
                next_lines = lines[i+1:i+3]
                args_found = False
                
                for j, next_line in enumerate(next_lines):
                    if '"' in next_line and ',' in next_line:
                        # Found arguments
                        fixed_line += next_line.strip() + "))"
                        args_found = True
                        # Skip the next line since we incorporated it
                        lines[i+1+j] = "# FIXED: line incorporated above"
                        break
                
                if not args_found:
                    # Default fallback
                    fixed_line += '"Navigation not available", "Navigation component"))'
                
                fixed_lines.append(fixed_line)
            
            # Fix other malformed safe_component_call lines
            elif "safe_component_call(" in line and not line.strip().endswith(')'):
                # Add missing closing parenthesis
                if line.strip().endswith('('):
                    fixed_lines.append(line + '"Fallback component", "Component"))')
                else:
                    fixed_lines.append(line + ')')
            
            # Skip lines we already incorporated
            elif line.strip().startswith("# FIXED:"):
                continue
                
            else:
                fixed_lines.append(line)
        
        # Write fixed content
        with open(file_path, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ Applied syntax fixes")
        
        # Test syntax
        try:
            with open(file_path, 'r') as f:
                test_content = f.read()
            compile(test_content, file_path, 'exec')
            print("✅ Syntax check passed!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error still exists: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False


def create_clean_layout_manager():
    """Create a clean, working layout_manager.py"""
    clean_layout_manager = '''# core/layout_manager.py - CLEAN VERSION
"""Layout management with safe component handling"""
from typing import Any
import logging

logger = logging.getLogger(__name__)


class LayoutManager:
    """Manages layout creation with safe component handling"""
    
    def __init__(self, component_registry):
        self.registry = component_registry
    
    def create_main_layout(self) -> Any:
        """Create main layout with safe components"""
        try:
            from dash import html, dcc
            
            # Create safe location component
            location_component = dcc.Location(id='url', refresh=False)
            
            # Get navbar safely
            navbar_component = self._get_safe_component('navbar', 'Navigation not available')
            
            # Create content area
            content_component = html.Div(
                id='page-content', 
                children=[self.create_dashboard_content()]
            )
            
            return html.Div([
                location_component,
                navbar_component,
                content_component
            ], className="dashboard")
            
        except ImportError:
            logger.error("Dash components not available")
            return None
        except Exception as e:
            logger.error(f"Error creating main layout: {e}")
            return None
    
    def create_dashboard_content(self) -> Any:
        """Create dashboard content with safe components"""
        try:
            from dash import html
            
            # Left panel with safe components
            left_panel = html.Div([
                self._get_safe_component('incident_alerts', 'Incident Alerts - Component not available')
            ], className="dashboard__left-panel")
            
            # Map panel with safe components  
            map_panel = html.Div([
                self._get_safe_component('map_panel', 'Map Panel - Component not available')
            ], className="dashboard__map-panel")
            
            # Bottom panel with safe components
            bottom_panel = html.Div([
                self._get_safe_component('bottom_panel', 'Bottom Panel - Component not available')
            ], className="dashboard__bottom-panel")
            
            return html.Div([
                html.Div([left_panel, map_panel], className="dashboard__top-row"),
                bottom_panel
            ], className="dashboard__content")
            
        except Exception as e:
            logger.error(f"Error creating dashboard content: {e}")
            try:
                from dash import html
                return html.Div([
                    html.H3("🏯 Yōsai Intel Dashboard"),
                    html.P("Dashboard running in safe mode"),
                    html.P(f"Error: {str(e)}")
                ], className="container")
            except ImportError:
                return None
    
    def _get_safe_component(self, component_name: str, fallback_text: str) -> Any:
        """Safely get a component, handling functions and fallbacks"""
        try:
            # Try to get component from registry
            component = self.registry.get_component(component_name)
            
            # If it's a function, call it to get the actual component
            if callable(component):
                try:
                    component = component()
                except Exception as e:
                    logger.warning(f"Error calling component function {component_name}: {e}")
                    component = None
            
            # If we have a valid component, return it
            if component is not None:
                return component
            
            # Otherwise, return safe fallback
            return self._create_fallback_component(fallback_text)
            
        except Exception as e:
            logger.error(f"Error getting component {component_name}: {e}")
            return self._create_fallback_component(f"{fallback_text} (Error: {str(e)})")
    
    def _create_fallback_component(self, text: str) -> Any:
        """Create a safe fallback component"""
        try:
            from dash import html
            return html.Div(
                text,
                className="alert alert-warning text-center",
                style={"margin": "1rem", "padding": "1rem"}
            )
        except ImportError:
            # Ultimate fallback
            return text
'''
    
    try:
        with open("core/layout_manager_clean.py", "w") as f:
            f.write(clean_layout_manager)
        print("✅ Created clean layout_manager_clean.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create clean layout manager: {e}")
        return False


def main():
    """Main fix function"""
    print("🔧 Fixing Layout Manager Syntax Error")
    print("=" * 40)
    
    if fix_layout_manager_syntax():
        print("\n🎉 Syntax fixed!")
        print("🚀 Try running the debugger again: python3 debug_json_error.py")
    else:
        print("\n❌ Automatic fix failed")
        print("🔧 Creating clean replacement...")
        
        if create_clean_layout_manager():
            print("✅ Clean layout manager created")
            print("\n🎯 Options:")
            print("1. Replace with clean version:")
            print("   cp core/layout_manager_clean.py core/layout_manager.py")
            print("2. Or use minimal app:")
            print("   python3 minimal_working_app.py")
        
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())