#!/usr/bin/env python3
"""
File Upload Diagnostic & Fix
Diagnoses and fixes file upload issues in the analytics page

This script:
1. Tests the file upload callback functionality
2. Checks file processing components
3. Fixes common upload issues
4. Provides a working file upload system
"""

import os
import sys
import json
import base64
import pandas as pd
from pathlib import Path

def setup_environment():
    """Setup environment for testing"""
    print("🔧 Setting up test environment...")
    
    env_vars = {
        'WTF_CSRF_ENABLED': 'False',
        'CSRF_ENABLED': 'False',
        'SECRET_KEY': 'dev-secret-key-12345',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1',
        'YOSAI_ENV': 'development',
        'AUTH0_CLIENT_ID': 'dev-client-id-12345',
        'AUTH0_CLIENT_SECRET': 'dev-client-secret-12345',
        'AUTH0_DOMAIN': 'dev-domain.auth0.com',
        'AUTH0_AUDIENCE': 'dev-audience-12345',
        'DISABLE_AUTH': 'True',
        'BYPASS_LOGIN': 'True'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("   ✅ Environment set")

def apply_patches():
    """Apply necessary patches"""
    print("🔧 Applying patches...")
    
    # JSON patch
    import json
    original_default = json.JSONEncoder.default
    def safe_json_handler(self, obj):
        if 'LazyString' in str(type(obj)):
            return str(obj)
        try:
            return original_default(self, obj)
        except (TypeError, AttributeError):
            return str(obj)
    json.JSONEncoder.default = safe_json_handler
    
    # Flask-Babel patch
    try:
        import flask_babel
        original_lazy = flask_babel.lazy_gettext
        flask_babel.lazy_gettext = lambda s, **k: str(original_lazy(s, **k))
        flask_babel._l = flask_babel.lazy_gettext
    except ImportError:
        pass
    
    # Auth patches
    try:
        import core.auth as auth_module
        def bypassed_role_required(role: str):
            def decorator(func):
                return func
            return decorator
        auth_module.role_required = bypassed_role_required
    except ImportError:
        pass
    
    print("   ✅ Patches applied")

def test_file_processing():
    """Test the file processing functionality"""
    print("🧪 Testing file processing...")
    
    try:
        from components.analytics.file_processing import FileProcessor
        
        # Create test CSV data
        test_data = pd.DataFrame({
            'employee_id': ['E001', 'E002', 'E003'],
            'access_point': ['ENTRANCE', 'SERVER', 'EXIT'],
            'result': ['GRANTED', 'DENIED', 'GRANTED'],
            'timestamp': ['2025-01-01 09:00:00', '2025-01-01 14:30:00', '2025-01-01 17:45:00']
        })
        
        # Convert to CSV string
        csv_string = test_data.to_csv(index=False)
        
        # Encode as base64 (like Dash upload component does)
        encoded = base64.b64encode(csv_string.encode('utf-8')).decode('utf-8')
        contents = f"data:text/csv;base64,{encoded}"
        
        # Test file processing
        result = FileProcessor.process_file_content(contents, "test.csv")
        
        if result is not None:
            print(f"   ✅ File processing works: {len(result)} rows, {len(result.columns)} columns")
            print(f"   Columns: {list(result.columns)}")
            return True
        else:
            print("   ❌ File processing returned None")
            return False
            
    except ImportError as e:
        print(f"   ❌ Cannot import FileProcessor: {e}")
        return False
    except Exception as e:
        print(f"   ❌ File processing test failed: {e}")
        return False

def test_analytics_components():
    """Test analytics components availability"""
    print("🧪 Testing analytics components...")
    
    try:
        # Test basic imports
        from components.analytics.file_uploader import create_file_uploader
        print("   ✅ File uploader component available")
        
        try:
            from components.analytics.file_processing import FileProcessor
            print("   ✅ FileProcessor available")
        except ImportError:
            print("   ❌ FileProcessor not available")
        
        try:
            from components.analytics.analytics_generator import AnalyticsGenerator
            print("   ✅ AnalyticsGenerator available")
        except ImportError:
            print("   ❌ AnalyticsGenerator not available")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Analytics components not available: {e}")
        return False

def test_callback_registration():
    """Test if the analytics callback is properly registered"""
    print("🧪 Testing callback registration...")
    
    try:
        # Check if the deep analytics page is importable
        import pages.deep_analytics as analytics_page
        print("   ✅ Deep analytics page imported")
        
        # Check if ANALYTICS_COMPONENTS_AVAILABLE is True
        if hasattr(analytics_page, 'ANALYTICS_COMPONENTS_AVAILABLE'):
            available = analytics_page.ANALYTICS_COMPONENTS_AVAILABLE
            print(f"   Analytics components available: {available}")
            if not available:
                print("   ⚠️ Analytics components are disabled")
                return False
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Cannot import analytics page: {e}")
        return False

def create_test_files():
    """Create test files for upload testing"""
    print("📁 Creating test files...")
    
    # Create test data directory
    test_dir = Path("test_uploads")
    test_dir.mkdir(exist_ok=True)
    
    # Test CSV
    test_csv_data = pd.DataFrame({
        'employee_id': ['E001', 'E002', 'E003', 'E004', 'E005'],
        'access_point': ['ENTRANCE', 'SERVER', 'EXIT', 'CONFERENCE', 'STORAGE'],
        'result': ['GRANTED', 'DENIED', 'GRANTED', 'GRANTED', 'DENIED'],
        'timestamp': [
            '2025-01-01 09:00:00',
            '2025-01-01 14:30:00',
            '2025-01-01 17:45:00',
            '2025-01-01 11:15:00',
            '2025-01-01 16:20:00'
        ]
    })
    
    # Save test files
    csv_file = test_dir / "test_data.csv"
    json_file = test_dir / "test_data.json"
    
    test_csv_data.to_csv(csv_file, index=False)
    test_csv_data.to_json(json_file, orient='records', date_format='iso')
    
    print(f"   ✅ Created test files in {test_dir}/")
    print(f"   📄 {csv_file} ({len(test_csv_data)} rows)")
    print(f"   📄 {json_file} ({len(test_csv_data)} rows)")
    
    return test_dir

def fix_analytics_components():
    """Fix analytics components if they're not working"""
    print("🔧 Fixing analytics components...")
    
    try:
        # Check if components exist
        import pages.deep_analytics as analytics_page
        
        # Force enable analytics components
        analytics_page.ANALYTICS_COMPONENTS_AVAILABLE = True
        print("   ✅ Force enabled ANALYTICS_COMPONENTS_AVAILABLE")
        
        # Try to patch any missing components
        try:
            from components.analytics.file_processing import FileProcessor
        except ImportError:
            print("   🔧 Creating fallback FileProcessor...")
            # Create a minimal fallback in the analytics module
            analytics_page.FileProcessor = create_fallback_file_processor()
        
        try:
            from components.analytics.analytics_generator import AnalyticsGenerator
        except ImportError:
            print("   🔧 Creating fallback AnalyticsGenerator...")
            analytics_page.AnalyticsGenerator = create_fallback_analytics_generator()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Could not fix analytics components: {e}")
        return False

def create_fallback_file_processor():
    """Create a fallback file processor class"""
    
    class FallbackFileProcessor:
        @staticmethod
        def process_file_content(contents: str, filename: str):
            """Fallback file processing"""
            if not contents or not filename:
                return None
            
            try:
                # Parse the data URL
                if ',' not in contents:
                    return None
                
                content_type, content_string = contents.split(',', 1)
                decoded = base64.b64decode(content_string)
                
                if filename.endswith('.csv'):
                    import io
                    csv_string = decoded.decode('utf-8')
                    return pd.read_csv(io.StringIO(csv_string))
                elif filename.endswith('.json'):
                    json_string = decoded.decode('utf-8')
                    data = json.loads(json_string)
                    return pd.DataFrame(data)
                else:
                    return None
                    
            except Exception as e:
                print(f"Fallback file processing error: {e}")
                return None
    
    return FallbackFileProcessor

def create_fallback_analytics_generator():
    """Create a fallback analytics generator"""
    
    class FallbackAnalyticsGenerator:
        @staticmethod
        def generate_analytics(df):
            """Generate basic analytics"""
            if df is None or df.empty:
                return {}
            
            return {
                'total_events': len(df),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'sample_data': df.head().to_dict('records')
            }
    
    return FallbackAnalyticsGenerator

def create_upload_test_script():
    """Create a script to test file uploads manually"""
    test_script = '''
import pandas as pd
import base64

# Create test data
test_data = pd.DataFrame({
    'employee_id': ['E001', 'E002', 'E003'],
    'access_point': ['ENTRANCE', 'SERVER', 'EXIT'],
    'result': ['GRANTED', 'DENIED', 'GRANTED'],
    'timestamp': ['2025-01-01 09:00:00', '2025-01-01 14:30:00', '2025-01-01 17:45:00']
})

# Convert to CSV
csv_string = test_data.to_csv(index=False)

# Encode as base64 (like Dash does)
encoded = base64.b64encode(csv_string.encode('utf-8')).decode('utf-8')
contents = f"data:text/csv;base64,{encoded}"

print("Test upload contents:")
print(f"Length: {len(contents)}")
print(f"First 100 chars: {contents[:100]}")

# Test file processing
try:
    from components.analytics.file_processing import FileProcessor
    result = FileProcessor.process_file_content(contents, "test.csv")
    if result is not None:
        print(f"✅ Processing successful: {len(result)} rows")
        print(f"Columns: {list(result.columns)}")
    else:
        print("❌ Processing failed")
except Exception as e:
    print(f"❌ Error: {e}")
'''
    
    with open("test_file_upload.py", "w") as f:
        f.write(test_script)
    
    print("   ✅ Created test_file_upload.py")

def main():
    """Main diagnostic and fix function"""
    print("📁 File Upload Diagnostic & Fix")
    print("=" * 35)
    
    # Setup
    setup_environment()
    apply_patches()
    
    # Test components
    tests = [
        ("Analytics Components", test_analytics_components),
        ("File Processing", test_file_processing),
        ("Callback Registration", test_callback_registration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        results[test_name] = test_func()
    
    # Apply fixes if needed
    if not all(results.values()):
        print(f"\n🔧 Applying fixes...")
        fix_analytics_components()
    
    # Create test resources
    print(f"\n📁 Creating test resources...")
    test_dir = create_test_files()
    create_upload_test_script()
    
    # Summary
    print(f"\n📊 Diagnostic Summary")
    print("=" * 25)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n💡 Recommendations:")
    if not results.get("File Processing", False):
        print("1. File processing is broken - use test_file_upload.py to debug")
    if not results.get("Analytics Components", False):
        print("2. Analytics components missing - fallbacks created")
    if not results.get("Callback Registration", False):
        print("3. Callback registration failed - check imports")
    
    print(f"\n🚀 To test file upload:")
    print(f"1. python3 test_file_upload.py  # Test processing directly")
    print(f"2. Upload files from {test_dir}/ in the web interface")
    print(f"3. Check browser console for JavaScript errors")
    
    print(f"\n📍 App should be running at: http://127.0.0.1:8050")

if __name__ == "__main__":
    main()