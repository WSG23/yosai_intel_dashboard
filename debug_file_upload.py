# debug_file_upload.py
#!/usr/bin/env python3
"""
Debug file upload system to find where files are stored
"""

def debug_file_upload_system():
    print("🔍 DEBUGGING FILE UPLOAD SYSTEM")
    print("=" * 50)
    
    try:
        # Test the file upload functions
        from pages.file_upload import get_uploaded_filenames, get_uploaded_data
        
        print("[INFO] Testing get_uploaded_filenames()...")
        filenames = get_uploaded_filenames()
        print(f"   Found filenames: {filenames}")
        
        print("[INFO] Testing get_uploaded_data()...")
        data = get_uploaded_data()
        print(f"   Found data keys: {list(data.keys()) if data else 'None'}")
        
        if data:
            for filename, df in data.items():
                print(f"   File: {filename} -> {len(df)} rows")
        
    except Exception as e:
        print(f"❌ Error testing file upload functions: {e}")
        import traceback
        print(traceback.format_exc())
    
    # Check if files exist in common upload directories
    print(f"\n📁 CHECKING COMMON UPLOAD DIRECTORIES:")
    import os
    
    common_dirs = [
        'uploads/',
        'temp/',
        'data/',
        'static/uploads/',
        '/tmp/',
        '.'  # current directory
    ]
    
    for dir_path in common_dirs:
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith(('.csv', '.json', '.xlsx', '.xls'))]
            if files:
                print(f"   ✅ {dir_path}: {files}")
            else:
                print(f"   📁 {dir_path}: (exists but no data files)")
        else:
            print(f"   ❌ {dir_path}: (doesn't exist)")
    
    # Check your specific files
    print(f"\n📄 CHECKING YOUR SPECIFIC FILES:")
    your_files = [
        "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv",
        "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/key_fob_access_log_sample.json"
    ]
    
    for file_path in your_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: EXISTS")
        else:
            print(f"   ❌ {file_path}: NOT FOUND")

if __name__ == "__main__":
    debug_file_upload_system()