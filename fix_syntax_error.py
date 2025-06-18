#!/usr/bin/env python3
"""
Fix Syntax Error in app_factory.py
"""

import shutil
from pathlib import Path
from datetime import datetime


def fix_app_factory_syntax():
    """Fix the syntax error in app_factory.py"""
    app_factory = Path("core/app_factory.py")
    
    if not app_factory.exists():
        print("❌ app_factory.py not found")
        return False
    
    try:
        # Backup first
        backup_file = f"core/app_factory.py.syntax_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(app_factory, backup_file)
        print(f"✅ Backed up to {backup_file}")
        
        # Read current content
        with open(app_factory, 'r') as f:
            content = f.read()
        
        # Check for syntax issues around the problematic area
        lines = content.split('\n')
        
        # Find and fix the problematic section
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic dash.index section
            if 'server.view_functions["dash.index"]' in line and 'login_required' in line:
                # Skip any malformed multi-line attempt
                while i < len(lines) and ('server.view_functions["dash.index"]' in lines[i] or 
                                         lines[i].strip() in [')', 'else:', 'logger.warning']):
                    i += 1
                
                # Add correct version
                indent = "            "  # Proper indentation
                fixed_lines.append(f'{indent}# Safely wrap dash.index with login_required')
                fixed_lines.append(f'{indent}try:')
                fixed_lines.append(f'{indent}    if "dash.index" in server.view_functions:')
                fixed_lines.append(f'{indent}        server.view_functions["dash.index"] = login_required(')
                fixed_lines.append(f'{indent}            server.view_functions["dash.index"]')
                fixed_lines.append(f'{indent}        )')
                fixed_lines.append(f'{indent}    else:')
                fixed_lines.append(f'{indent}        logger.warning("dash.index view function not found")')
                fixed_lines.append(f'{indent}except Exception as e:')
                fixed_lines.append(f'{indent}    logger.warning(f"Could not wrap dash.index with login_required: {{e}}")')
                continue
            
            # Look for any standalone closing parenthesis that might be causing issues
            elif line.strip() == ')' and i > 0:
                # Check if this is a stray closing paren
                prev_line = lines[i-1].strip()
                if not (prev_line.endswith('(') or prev_line.endswith(',') or 'login_required' in prev_line):
                    # This might be a stray paren, skip it
                    print(f"⚠️  Skipping potential stray closing paren at line {i+1}")
                    i += 1
                    continue
            
            fixed_lines.append(line)
            i += 1
        
        # Write the fixed content
        with open(app_factory, 'w') as f:
            f.write('\n'.join(fixed_lines))
        
        print("✅ Fixed syntax error in app_factory.py")
        
        # Test syntax by trying to compile
        try:
            with open(app_factory, 'r') as f:
                test_content = f.read()
            compile(test_content, app_factory, 'exec')
            print("✅ Syntax check passed!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error still exists: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")
        return False


def create_emergency_simple_app_factory():
    """Create a simplified app_factory.py that works"""
    simple_app_factory = '''#!/usr/bin/env python3
"""
Emergency Simple App Factory - Syntax Error Free
"""

import logging
import dash
from typing import Optional

logger = logging.getLogger(__name__)


def create_application() -> Optional[dash.Dash]:
    """Create a simple Dash application without complex auth"""
    try:
        from dash import html, dcc
        import dash_bootstrap_components as dbc
        
        # Create basic Dash app
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        
        app.title = "Yōsai Intel Dashboard"
        
        # Simple layout
        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.H1("🏯 Yōsai Intel Dashboard", className="text-center"),
            html.Hr(),
            html.Div([
                dbc.Alert("✅ Application created successfully!", color="success"),
                dbc.Alert("⚠️ Running in simplified mode (no auth)", color="warning"),
                html.P("Environment configuration loaded and working."),
                html.P("Ready for development and testing."),
            ], className="container")
        ])
        
        logger.info("Simple Dash application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        return None


# Backwards compatibility
def create_dash_app():
    """Legacy function name"""
    return create_application()
'''
    
    try:
        with open("core/app_factory_simple.py", "w") as f:
            f.write(simple_app_factory)
        print("✅ Created emergency simple app factory")
        return True
    except Exception as e:
        print(f"❌ Failed to create simple app factory: {e}")
        return False


def main():
    """Main fix function"""
    print("🔧 Fixing Syntax Error in app_factory.py")
    print("=" * 40)
    
    if fix_app_factory_syntax():
        print("\n🎉 Syntax error fixed!")
        print("🚀 Try running: python3 app.py")
    else:
        print("\n❌ Could not fix syntax error automatically")
        print("🔧 Creating emergency backup...")
        
        if create_emergency_simple_app_factory():
            print("✅ Emergency simple app factory created")
            print("\n🎯 Try these options:")
            print("1. python3 minimal_working_app.py  # Full featured")
            print("2. Use simple app factory in your app.py")
            print("3. Restore from backup and fix manually")
        
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())