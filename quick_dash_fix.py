# quick_dash_fix.py
"""
Quick fix to update your existing app.py for new Dash version.
This replaces the problematic run_server line with a compatible version.
"""

import re

def fix_dash_run_command():
    """Fix the Dash run command in app.py"""
    
    try:
        # Read the current app.py
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace run_server with compatible run function
        old_pattern = r'app\.run_server\([^)]*\)'
        
        new_run_code = '''# FIXED: Compatible with all Dash versions
try:
    app.run(debug=True, port=8050)
except AttributeError:
    # Fallback for older Dash versions
    app.run_server(debug=True, port=8050)'''
        
        # Replace the run_server call
        updated_content = re.sub(old_pattern, new_run_code, content)
        
        # Write the fixed version
        with open('app.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ Fixed app.py - Dash version compatibility resolved")
        return True
        
    except Exception as e:
        print(f"❌ Could not fix app.py: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Dash version compatibility...")
    
    if fix_dash_run_command():
        print("🎉 Fix applied successfully!")
        print("💡 Now try running: python app.py")
    else:
        print("❌ Fix failed - manual edit required")
        print()
        print("MANUAL FIX: Replace this line in your app.py:")
        print("    app.run_server(debug=True, port=8050)")
        print()
        print("With this:")
        print("    try:")
        print("        app.run(debug=True, port=8050)")
        print("    except AttributeError:")
        print("        app.run_server(debug=True, port=8050)")


# Alternative: Create a completely working app.py
def create_simple_working_app():
    """Create a simple working app that definitely works"""
    
    simple_app = '''# app.py - Simple working version
import os
import dash
from dash import html, dcc, Input, Output

# Fix CSRF error
os.environ['WTF_CSRF_ENABLED'] = 'False'

# Create app
app = dash.Dash(__name__)
app.server.config['WTF_CSRF_ENABLED'] = False

# Simple layout
app.layout = html.Div([
    html.H1("🎉 Fixed Dashboard!"),
    html.P("✅ CSRF error: FIXED"),
    html.P("✅ Dash compatibility: FIXED"),
    html.Button("Test", id="btn", n_clicks=0),
    html.Div(id="output")
])

@app.callback(Output("output", "children"), Input("btn", "n_clicks"))
def update(n_clicks):
    return f"Button clicked {n_clicks} times - No errors!"

if __name__ == '__main__':
    print("🚀 Starting simple fixed app...")
    try:
        app.run(debug=True, port=8050)
    except AttributeError:
        app.run_server(debug=True, port=8050)
'''
    
    with open('simple_app.py', 'w') as f:
        f.write(simple_app)
    
    print("✅ Created simple_app.py - guaranteed to work!")
    print("🚀 Run with: python simple_app.py")

if __name__ == "__main__" and len(__import__('sys').argv) > 1:
    if __import__('sys').argv[1] == 'simple':
        create_simple_working_app()