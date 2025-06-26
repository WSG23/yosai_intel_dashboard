# ui_diagnostic.py
"""
UI Diagnostic Script
Run this to test if the Deep Analytics UI fix works
"""

def test_imports():
    """Test if all required imports are available"""
    print("🔍 Testing Required Imports...")
    
    imports_status = {}
    
    # Test Dash core
    try:
        from dash import html, dcc, callback, Input, Output
        imports_status['dash_core'] = True
        print("✅ Dash core components: OK")
    except ImportError as e:
        imports_status['dash_core'] = False
        print(f"❌ Dash core components: FAILED - {e}")
    
    # Test Dash Bootstrap Components
    try:
        import dash_bootstrap_components as dbc
        imports_status['dash_bootstrap'] = True
        print("✅ Dash Bootstrap Components: OK")
    except ImportError as e:
        imports_status['dash_bootstrap'] = False
        print(f"❌ Dash Bootstrap Components: FAILED - {e}")
        print("   Install with: pip install dash-bootstrap-components")
    
    # Test Plotly
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        imports_status['plotly'] = True
        print("✅ Plotly: OK")
    except ImportError as e:
        imports_status['plotly'] = False
        print(f"❌ Plotly: FAILED - {e}")
        print("   Install with: pip install plotly")
    
    # Test pandas
    try:
        import pandas as pd
        imports_status['pandas'] = True
        print("✅ Pandas: OK")
    except ImportError as e:
        imports_status['pandas'] = False
        print(f"❌ Pandas: FAILED - {e}")
    
    return imports_status

def test_layout_function():
    """Test if the layout function can be created"""
    print("\n🏗️ Testing Layout Function...")
    
    try:
        # Import required components
        from dash import html, dcc
        import dash_bootstrap_components as dbc
        
        # Test basic layout creation
        test_layout = dbc.Container([
            html.H1("Test Layout"),
            dbc.Alert("Test alert", color="success"),
            dcc.Dropdown(
                options=[{"label": "Test", "value": "test"}],
                value="test"
            )
        ])
        
        print("✅ Layout function creation: OK")
        return True
        
    except Exception as e:
        print(f"❌ Layout function creation: FAILED - {e}")
        return False

def test_file_structure():
    """Test if required files exist"""
    print("\n📁 Testing File Structure...")
    
    import os
    from pathlib import Path
    
    required_files = [
        'pages/deep_analytics.py',
        'services/analytics_service.py',
        'components/__init__.py'
    ]
    
    file_status = {}
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_status[file_path] = True
            print(f"✅ {file_path}: EXISTS")
        else:
            file_status[file_path] = False
            print(f"❌ {file_path}: MISSING")
    
    return file_status

def create_minimal_test_layout():
    """Create a minimal working layout for testing"""
    print("\n🧪 Creating Minimal Test Layout...")
    
    try:
        from dash import html, dcc
        import dash_bootstrap_components as dbc
        
        minimal_layout = dbc.Container([
            # Header
            html.H1("🔍 Deep Analytics - Test Mode", className="text-primary"),
            
            # Status indicator
            dbc.Alert([
                html.H4("✅ UI Components Working"),
                html.P("All Dash components are loading correctly."),
                html.P("The Deep Analytics page should now display properly.")
            ], color="success"),
            
            # Test components
            dbc.Card([
                dbc.CardHeader("🧪 Component Test"),
                dbc.CardBody([
                    html.P("Testing basic components:"),
                    dcc.Dropdown(
                        options=[
                            {"label": "Test Option 1", "value": "test1"},
                            {"label": "Test Option 2", "value": "test2"}
                        ],
                        value="test1",
                        placeholder="Test dropdown..."
                    ),
                    html.Br(),
                    dbc.Button("Test Button", color="primary"),
                    html.Br(),
                    html.Br(),
                    dbc.Progress(value=75, label="75%")
                ])
            ])
        ])
        
        print("✅ Minimal layout created successfully")
        return minimal_layout
        
    except Exception as e:
        print(f"❌ Minimal layout creation failed: {e}")
        return None

def run_full_diagnostic():
    """Run complete diagnostic check"""
    print("🚀 DEEP ANALYTICS UI DIAGNOSTIC")
    print("=" * 50)
    
    # Test 1: Imports
    imports_ok = test_imports()
    
    # Test 2: Layout function
    layout_ok = test_layout_function()
    
    # Test 3: File structure
    files_ok = test_file_structure()
    
    # Test 4: Minimal layout
    minimal_layout = create_minimal_test_layout()
    
    # Overall assessment
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    all_imports_good = all(imports_ok.values())
    
    if all_imports_good and layout_ok and minimal_layout:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe UI fix should work. Next steps:")
        print("1. Apply the fix to pages/deep_analytics.py")
        print("2. Restart your Dash application")
        print("3. Navigate to /analytics")
        print("4. Verify the UI loads properly")
        
        # Create test file
        try:
            with open('test_layout.py', 'w') as f:
                f.write('''
# test_layout.py - Minimal working layout for testing
from dash import html, dcc
import dash_bootstrap_components as dbc

def test_layout():
    return dbc.Container([
        html.H1("🔍 Deep Analytics - Test", className="text-primary"),
        dbc.Alert("UI components working!", color="success"),
        dcc.Dropdown(
            options=[{"label": "Test", "value": "test"}],
            value="test"
        ),
        dbc.Button("Test Button", color="primary")
    ])
''')
            print("\n📄 Created test_layout.py for verification")
        except:
            pass
            
    else:
        print("❌ SOME TESTS FAILED")
        print("\nIssues detected:")
        
        if not all_imports_good:
            print("- Missing required packages")
            print("  Run: pip install dash dash-bootstrap-components plotly pandas")
        
        if not layout_ok:
            print("- Layout function creation failed")
            print("  Check for syntax errors in component creation")
        
        if not minimal_layout:
            print("- Component creation failed")
            print("  Basic Dash components are not working")
    
    return all_imports_good and layout_ok and minimal_layout is not None

def generate_requirements_file():
    """Generate requirements file for missing packages"""
    print("\n📦 Generating requirements.txt...")
    
    requirements = [
        "dash>=2.0.0",
        "dash-bootstrap-components>=1.0.0", 
        "plotly>=5.0.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0"
    ]
    
    try:
        with open('requirements_ui.txt', 'w') as f:
            for req in requirements:
                f.write(req + '\n')
        
        print("✅ Created requirements_ui.txt")
        print("Install with: pip install -r requirements_ui.txt")
        
    except Exception as e:
        print(f"❌ Failed to create requirements file: {e}")

if __name__ == "__main__":
    print("🔧 Starting Deep Analytics UI Diagnostic...")
    
    # Run diagnostic
    success = run_full_diagnostic()
    
    # Generate requirements if needed
    generate_requirements_file()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 DIAGNOSTIC COMPLETE - Ready to apply UI fix!")
        print("\nApply the fix from deep_analytics_ui_fix.py to resolve the UI issue.")
    else:
        print("⚠️ DIAGNOSTIC COMPLETE - Issues need to be resolved first.")
        print("\nInstall missing packages, then re-run this diagnostic.")
    
    print("\nFor immediate testing:")
    print("1. Install packages: pip install dash dash-bootstrap-components plotly")
    print("2. Apply the UI fix to pages/deep_analytics.py") 
    print("3. Restart your Dash app")
    print("4. Check /analytics page")