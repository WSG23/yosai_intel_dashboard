#!/usr/bin/env python3
"""
Simple File Upload Fix
Creates a working file upload system with minimal dependencies

This replaces the complex analytics system with a simple working version.
"""

import os
import sys
import json
import base64
import pandas as pd
import io
from pathlib import Path

def setup_environment():
    """Setup environment"""
    env_vars = {
        'WTF_CSRF_ENABLED': 'False',
        'DISABLE_AUTH': 'True',
        'BYPASS_LOGIN': 'True',
        'SECRET_KEY': 'dev-secret',
        'FLASK_ENV': 'development',
        'AUTH0_CLIENT_ID': 'dev-client-id',
        'AUTH0_CLIENT_SECRET': 'dev-client-secret',
        'AUTH0_DOMAIN': 'dev-domain.auth0.com',
        'AUTH0_AUDIENCE': 'dev-audience'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value

def apply_basic_patches():
    """Apply basic patches"""
    # JSON patch
    import json
    original_default = json.JSONEncoder.default
    def safe_json(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        try:
            return original_default(self, obj)
        except:
            return str(obj)
    json.JSONEncoder.default = safe_json
    
    # Flask-Babel patch
    try:
        import flask_babel
        orig = flask_babel.lazy_gettext
        flask_babel.lazy_gettext = lambda s, **k: str(orig(s, **k))
        flask_babel._l = flask_babel.lazy_gettext
    except ImportError:
        pass
    
    # Auth bypass
    try:
        import core.auth
        core.auth.role_required = lambda role: lambda f: f
    except ImportError:
        pass

def create_simple_file_processor():
    """Create a simple, working file processor"""
    
    class SimpleFileProcessor:
        @staticmethod
        def process_file_content(contents: str, filename: str):
            """Simple file processing that actually works"""
            print(f"Processing file: {filename}")
            
            if not contents or not filename:
                print("No contents or filename")
                return None
            
            try:
                # Parse data URL
                if 'base64,' not in contents:
                    print("Invalid contents format")
                    return None
                
                # Extract base64 data
                encoded_data = contents.split('base64,')[1]
                decoded_data = base64.b64decode(encoded_data)
                
                # Process based on file type
                if filename.lower().endswith('.csv'):
                    csv_string = decoded_data.decode('utf-8')
                    df = pd.read_csv(io.StringIO(csv_string))
                    print(f"CSV processed: {len(df)} rows, {len(df.columns)} columns")
                    return df
                    
                elif filename.lower().endswith('.json'):
                    json_string = decoded_data.decode('utf-8')
                    data = json.loads(json_string)
                    df = pd.DataFrame(data)
                    print(f"JSON processed: {len(df)} rows, {len(df.columns)} columns")
                    return df
                    
                else:
                    print(f"Unsupported file type: {filename}")
                    return None
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                return None
    
    return SimpleFileProcessor

def create_simple_analytics():
    """Create simple analytics generator"""
    
    class SimpleAnalytics:
        @staticmethod
        def generate_analytics(df):
            """Generate simple analytics"""
            if df is None or df.empty:
                return {}
            
            analytics = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'sample_data': df.head(5).to_dict('records'),
                'summary': df.describe().to_dict() if df.select_dtypes(include='number').shape[1] > 0 else {}
            }
            
            return analytics
    
    return SimpleAnalytics

def patch_analytics_page():
    """Patch the analytics page with working components"""
    print("🔧 Patching analytics page with simple components...")
    
    try:
        import pages.deep_analytics as analytics_page
        
        # Enable components
        analytics_page.ANALYTICS_COMPONENTS_AVAILABLE = True
        print("   ✅ Enabled ANALYTICS_COMPONENTS_AVAILABLE")
        
        # Replace with simple working components
        analytics_page.FileProcessor = create_simple_file_processor()
        analytics_page.AnalyticsGenerator = create_simple_analytics()
        print("   ✅ Replaced FileProcessor and AnalyticsGenerator")
        
        # Patch the callback to be simpler
        def create_simple_callback(app):
            """Create a simple working callback"""
            
            @app.callback(
                [
                    app.callback.Output("upload-status", "children"),
                    app.callback.Output("uploaded-data-store", "data"),
                    app.callback.Output("analytics-results", "children"),
                ],
                app.callback.Input("analytics-file-upload", "contents"),
                app.callback.State("analytics-file-upload", "filename"),
                prevent_initial_call=True,
            )
            def simple_process_files(contents_list, filename_list):
                """Simple file processing callback"""
                
                if not contents_list or not filename_list:
                    return [], {}, []
                
                # Ensure lists
                if isinstance(contents_list, str):
                    contents_list = [contents_list]
                if isinstance(filename_list, str):
                    filename_list = [filename_list]
                
                from dash import html
                import dash_bootstrap_components as dbc
                
                status_messages = []
                all_data = {}
                results = []
                
                for contents, filename in zip(contents_list, filename_list):
                    print(f"\n📁 Processing: {filename}")
                    
                    # Process file
                    df = analytics_page.FileProcessor.process_file_content(contents, filename)
                    
                    if df is not None:
                        # Success
                        status_messages.append(
                            dbc.Alert([
                                html.I(className="fas fa-check-circle me-2"),
                                f"✅ Successfully processed {filename}: {len(df)} rows, {len(df.columns)} columns"
                            ], color="success", className="mb-2")
                        )
                        
                        # Store data
                        all_data[filename] = {
                            'data': df.to_dict('records'),
                            'filename': filename,
                            'rows': len(df),
                            'columns': list(df.columns)
                        }
                        
                        # Generate analytics
                        analytics = analytics_page.AnalyticsGenerator.generate_analytics(df)
                        
                        # Create results display
                        results.append(
                            dbc.Card([
                                dbc.CardHeader(html.H5(f"📊 {filename}")),
                                dbc.CardBody([
                                    html.P(f"Rows: {analytics.get('total_rows', 0)}"),
                                    html.P(f"Columns: {analytics.get('total_columns', 0)}"),
                                    html.P(f"Column names: {', '.join(analytics.get('columns', []))}"),
                                    html.Details([
                                        html.Summary("📋 Sample Data"),
                                        html.Pre(json.dumps(analytics.get('sample_data', [])[:3], indent=2))
                                    ])
                                ])
                            ], className="mb-3")
                        )
                        
                    else:
                        # Error
                        status_messages.append(
                            dbc.Alert([
                                html.I(className="fas fa-times-circle me-2"),
                                f"❌ Failed to process {filename}"
                            ], color="danger", className="mb-2")
                        )
                
                return status_messages, all_data, results
            
            return simple_process_files
        
        # Store the callback creator
        analytics_page.create_simple_callback = create_simple_callback
        print("   ✅ Created simple callback function")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to patch analytics page: {e}")
        return False

def register_simple_callback(app):
    """Register a simple working callback"""
    print("📝 Registering simple file upload callback...")
    
    try:
        import pages.deep_analytics as analytics_page
        
        if hasattr(analytics_page, 'create_simple_callback'):
            callback_func = analytics_page.create_simple_callback(app)
            print("   ✅ Simple callback registered")
            return True
        else:
            print("   ❌ create_simple_callback not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to register callback: {e}")
        return False

def create_test_files():
    """Create test files for upload"""
    print("📁 Creating test files...")
    
    # Create test data
    test_data = pd.DataFrame({
        'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
        'access_point': ['MAIN_ENTRANCE', 'SERVER_ROOM', 'CONFERENCE_A', 'PARKING_GATE', 'STORAGE'],
        'access_result': ['GRANTED', 'DENIED', 'GRANTED', 'GRANTED', 'DENIED'],
        'timestamp': [
            '2025-01-15 09:00:00',
            '2025-01-15 09:15:00', 
            '2025-01-15 09:30:00',
            '2025-01-15 09:45:00',
            '2025-01-15 10:00:00'
        ],
        'badge_number': ['B001', 'B002', 'B003', 'B004', 'B005'],
        'department': ['IT', 'HR', 'FINANCE', 'OPERATIONS', 'SECURITY']
    })
    
    # Create test directory
    test_dir = Path("sample_uploads")
    test_dir.mkdir(exist_ok=True)
    
    # Save as CSV
    csv_file = test_dir / "sample_access_data.csv"
    test_data.to_csv(csv_file, index=False)
    
    # Save as JSON
    json_file = test_dir / "sample_access_data.json"
    test_data.to_json(json_file, orient='records', date_format='iso')
    
    print(f"   ✅ Created test files in {test_dir}/")
    print(f"   📄 {csv_file} - CSV format")
    print(f"   📄 {json_file} - JSON format")
    
    return test_dir

def main():
    """Main function to fix file upload"""
    print("📁 Simple File Upload Fix")
    print("=" * 30)
    
    try:
        # Setup
        setup_environment()
        apply_basic_patches()
        
        # Patch analytics components
        if patch_analytics_page():
            print("✅ Analytics page patched successfully")
        else:
            print("❌ Analytics page patching failed")
            return 1
        
        # Create test files
        test_dir = create_test_files()
        
        # Import and create app
        print("\n🚀 Creating app with simple file upload...")
        from core.app_factory import create_application
        
        app = create_application()
        if app is None:
            print("❌ App creation failed")
            return 1
        
        # Register simple callback (replace the complex one)
        if register_simple_callback(app):
            print("✅ Simple callback registered")
        else:
            print("⚠️ Callback registration uncertain")
        
        # Configure app
        if hasattr(app, 'server'):
            app.server.config.update({
                'WTF_CSRF_ENABLED': False,
                'TESTING': True,
                'SECRET_KEY': 'dev-secret'
            })
        
        print(f"\n🌐 Starting server at http://127.0.0.1:8050")
        print(f"📁 Test files available in: {test_dir}/")
        print(f"🔧 Simple file upload system enabled")
        print(f"📤 Try uploading CSV or JSON files")
        print(f"🛑 Press Ctrl+C to stop\n")
        
        app.run(debug=True, host='127.0.0.1', port=8050)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())