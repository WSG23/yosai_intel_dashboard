#!/usr/bin/env python3
"""
Simple File Type Fix
Quick fix to enable JSON and Excel uploads

This is a minimal fix that just enables the file types without complex processing.
"""

import os
import sys
import json
import base64
import pandas as pd
import io

def setup_environment():
    """Setup environment"""
    env_vars = {
        'WTF_CSRF_ENABLED': 'False',
        'DISABLE_AUTH': 'True',
        'SECRET_KEY': 'dev-secret',
        'FLASK_ENV': 'development',
        'AUTH0_CLIENT_ID': 'dev-client-id',
        'AUTH0_CLIENT_SECRET': 'dev-client-secret',
        'AUTH0_DOMAIN': 'dev-domain.auth0.com',
        'AUTH0_AUDIENCE': 'dev-audience'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value

def apply_patches():
    """Apply basic patches"""
    import json
    original_default = json.JSONEncoder.default
    def safe_json_handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        try:
            return original_default(self, obj)
        except:
            return str(obj)
    json.JSONEncoder.default = safe_json_handler
    
    try:
        import flask_babel
        orig = flask_babel.lazy_gettext
        flask_babel.lazy_gettext = lambda s, **k: str(orig(s, **k))
        flask_babel._l = flask_babel.lazy_gettext
    except ImportError:
        pass
    
    try:
        import core.auth
        core.auth.role_required = lambda role: lambda f: f
    except ImportError:
        pass

def create_simple_file_processor():
    """Create simple file processor that handles all types"""
    
    class SimpleFileProcessor:
        @staticmethod
        def process_file_content(contents: str, filename: str):
            """Process any file type - CSV, JSON, or Excel"""
            print(f"📁 Processing: {filename}")
            
            if not contents or not filename:
                return None
            
            try:
                # Get file extension
                file_ext = filename.lower().split('.')[-1]
                print(f"   File type: {file_ext}")
                
                # Extract and decode data
                if 'base64,' not in contents:
                    print("   ❌ Invalid format")
                    return None
                
                encoded_data = contents.split('base64,')[1]
                decoded_data = base64.b64decode(encoded_data)
                
                # Process based on file type
                if file_ext == 'csv':
                    return SimpleFileProcessor._process_csv(decoded_data)
                elif file_ext == 'json':
                    return SimpleFileProcessor._process_json(decoded_data)
                elif file_ext in ['xlsx', 'xls']:
                    return SimpleFileProcessor._process_excel(decoded_data)
                else:
                    print(f"   ⚠️ Trying to process {file_ext} as CSV...")
                    return SimpleFileProcessor._process_csv(decoded_data)
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return None
        
        @staticmethod
        def _process_csv(decoded_data):
            """Process CSV data"""
            try:
                csv_string = decoded_data.decode('utf-8')
                df = pd.read_csv(io.StringIO(csv_string))
                print(f"   ✅ CSV: {len(df)} rows, {len(df.columns)} columns")
                return df
            except Exception as e:
                print(f"   ❌ CSV error: {e}")
                return None
        
        @staticmethod
        def _process_json(decoded_data):
            """Process JSON data"""
            try:
                json_string = decoded_data.decode('utf-8')
                data = json.loads(json_string)
                
                # Convert to DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.DataFrame([data])
                else:
                    df = pd.DataFrame(data)
                
                print(f"   ✅ JSON: {len(df)} rows, {len(df.columns)} columns")
                return df
            except Exception as e:
                print(f"   ❌ JSON error: {e}")
                return None
        
        @staticmethod
        def _process_excel(decoded_data):
            """Process Excel data"""
            try:
                excel_file = io.BytesIO(decoded_data)
                df = pd.read_excel(excel_file, engine='openpyxl')
                print(f"   ✅ Excel: {len(df)} rows, {len(df.columns)} columns")
                return df
            except ImportError:
                print("   ❌ Excel support not installed (pip install openpyxl)")
                return None
            except Exception as e:
                print(f"   ❌ Excel error: {e}")
                return None
    
    return SimpleFileProcessor

def patch_file_uploader():
    """Update file uploader to accept all file types"""
    print("🔧 Patching file uploader to accept all types...")
    
    try:
        # Import and patch the file uploader
        from components.analytics.file_uploader import create_file_uploader
        
        # Create new uploader function
        def enhanced_file_uploader(upload_id: str = 'analytics-file-upload'):
            from dash import html, dcc
            import dash_bootstrap_components as dbc
            
            return html.Div([dbc.Card([
                dbc.CardHeader([
                    html.H4("📁 Multi-Format Data Upload", className="mb-0"),
                    html.Small("Upload CSV, JSON, or Excel files", className="text-muted")
                ]),
                dbc.CardBody([
                    dcc.Upload(
                        id=upload_id,
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                            html.H5("Drag and Drop or Click to Select Files"),
                            html.Div([
                                html.P("📊 CSV (.csv)", className="mb-1"),
                                html.P("📋 JSON (.json)", className="mb-1"),
                                html.P("📈 Excel (.xlsx, .xls)", className="mb-1"),
                            ], className="mt-2"),
                            html.P("Max size: 100MB", className="text-muted small")
                        ]),
                        style={
                            'width': '100%',
                            'height': '220px',
                            'lineHeight': '60px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'backgroundColor': '#f8f9fa',
                            'cursor': 'pointer'
                        },
                        multiple=True,
                        # Accept all file types explicitly
                        accept='.csv,.json,.xlsx,.xls,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv,text/json'
                    ),
                    html.Div(id='upload-status', className="mt-3"),
                    html.Div(id='file-info', className="mt-3")
                ])
            ], className="mb-4")])
        
        # Replace the original function
        import components.analytics.file_uploader as uploader_module
        uploader_module.create_file_uploader = enhanced_file_uploader
        
        print("   ✅ File uploader patched to accept all types")
        return True
        
    except Exception as e:
        print(f"   ❌ Uploader patch failed: {e}")
        return False

def patch_analytics_page():
    """Patch analytics page with simple file processor"""
    print("🔧 Patching analytics with multi-format processor...")
    
    try:
        import pages.deep_analytics as analytics_page
        
        # Replace FileProcessor
        analytics_page.FileProcessor = create_simple_file_processor()
        print("   ✅ FileProcessor updated for all file types")
        
        # Ensure components are enabled
        analytics_page.ANALYTICS_COMPONENTS_AVAILABLE = True
        
        return True
        
    except Exception as e:
        print(f"   ❌ Analytics patch failed: {e}")
        return False

def create_quick_test_files():
    """Create quick test files"""
    print("📁 Creating test files...")
    
    from pathlib import Path
    
    test_dir = Path("quick_test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Test data
    test_data = [
        {"name": "Alice", "age": 25, "department": "IT"},
        {"name": "Bob", "age": 30, "department": "HR"},
        {"name": "Charlie", "age": 35, "department": "Finance"}
    ]
    
    # CSV
    csv_file = test_dir / "test.csv"
    df = pd.DataFrame(test_data)
    df.to_csv(csv_file, index=False)
    print(f"   ✅ {csv_file}")
    
    # JSON
    json_file = test_dir / "test.json"
    with open(json_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    print(f"   ✅ {json_file}")
    
    # Excel (if possible)
    try:
        excel_file = test_dir / "test.xlsx"
        df.to_excel(excel_file, index=False)
        print(f"   ✅ {excel_file}")
    except:
        print("   ⚠️ Excel file not created (install openpyxl)")
    
    return test_dir

def main():
    """Simple fix for file type support"""
    print("📁 Simple File Type Fix")
    print("=" * 25)
    
    try:
        # Setup
        setup_environment()
        apply_patches()
        
        # Patch components
        patch_file_uploader()
        patch_analytics_page()
        
        # Create test files
        test_dir = create_quick_test_files()
        
        # Test processing
        print("\n🧪 Quick test...")
        try:
            import pages.deep_analytics as analytics_page
            
            # Test JSON processing
            test_json = json.dumps([{"name": "test", "value": 123}])
            encoded = base64.b64encode(test_json.encode()).decode()
            contents = f"data:application/json;base64,{encoded}"
            
            result = analytics_page.FileProcessor.process_file_content(contents, "test.json")
            if result is not None:
                print("   ✅ JSON processing works")
            else:
                print("   ❌ JSON processing failed")
                
        except Exception as e:
            print(f"   ⚠️ Test error: {e}")
        
        # Start app
        print("\n🚀 Starting app with multi-format support...")
        from core.app_factory import create_application
        
        app = create_application()
        if app:
            if hasattr(app, 'server'):
                app.server.config.update({
                    'WTF_CSRF_ENABLED': False,
                    'TESTING': True,
                    'SECRET_KEY': 'dev-secret'
                })
            
            print(f"\n🌐 Server: http://127.0.0.1:8050")
            print(f"📂 Test files: {test_dir}/")
            print(f"✅ Now supports: CSV, JSON, Excel")
            print(f"🛑 Ctrl+C to stop\n")
            
            app.run(debug=True, host='127.0.0.1', port=8050)
        else:
            print("❌ App creation failed")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())