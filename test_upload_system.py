# test_upload_system.py
"""
Test Script for File Upload System
Run this to verify the upload fix is working correctly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path


def create_test_data():
    """Create test data that matches expected format"""
    print("📊 Creating test data...")
    
    # Generate sample access control data
    np.random.seed(42)
    n_records = 1000
    
    # Date range: last 30 days
    start_date = datetime.now() - timedelta(days=30)
    dates = pd.date_range(start=start_date, periods=n_records, freq='15min')
    
    # Generate realistic data
    users = [f"USER{i:04d}" for i in range(1, 51)]
    doors = ["DOOR001", "DOOR002", "DOOR003", "DOOR004", "DOOR005"]
    access_results = ["Granted", "Denied"]
    badge_statuses = ["Valid", "Invalid", "Expired"]
    
    data = {
        'timestamp': np.random.choice(dates, n_records),
        'person_id': np.random.choice(users, n_records),
        'door_id': np.random.choice(doors, n_records),
        'access_result': np.random.choice(access_results, n_records, p=[0.85, 0.15]),
        'badge_status': np.random.choice(badge_statuses, n_records, p=[0.8, 0.15, 0.05]),
        'device_status': np.random.choice(['normal', 'maintenance'], n_records, p=[0.95, 0.05])
    }
    
    df = pd.DataFrame(data)
    df = df.sort_values('timestamp').reset_index(drop=True)
    df['event_id'] = [f"EVT{i:06d}" for i in range(len(df))]
    
    return df


def save_test_files():
    """Save test files in different formats"""
    print("💾 Saving test files...")
    
    # Create temp directory
    test_dir = Path("temp/test_files")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate test data
    df = create_test_data()
    
    # Save as CSV
    csv_path = test_dir / "test_access_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved CSV: {csv_path}")
    
    # Save as JSON
    json_path = test_dir / "test_access_data.json"
    df.to_json(json_path, orient='records', date_format='iso')
    print(f"✅ Saved JSON: {json_path}")
    
    # Save as Excel
    try:
        excel_path = test_dir / "test_access_data.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"✅ Saved Excel: {excel_path}")
    except ImportError:
        print("⚠️ Excel support not available (openpyxl not installed)")
    
    return {
        'csv': csv_path,
        'json': json_path,
        'excel': excel_path if 'excel_path' in locals() else None,
        'dataframe': df
    }


def test_upload_store():
    """Test the upload data store functionality"""
    print("\n🧪 Testing Upload Data Store...")
    
    try:
        # Import the fixed upload store
        import sys
        sys.path.append('.')
        
        from file_upload_fix import UploadedDataStore
        
        store = UploadedDataStore()
        
        test_df = create_test_data()
        
        store.add_file("test_data.csv", test_df)
        print(f"✅ Added test file: {len(test_df)} rows")
        
        retrieved_df = store.get_file("test_data.csv")
        if retrieved_df is not None and len(retrieved_df) == len(test_df):
            print("✅ File retrieval successful")
        else:
            print("❌ File retrieval failed")
        
        filenames = store.get_filenames()
        print(f"✅ Available files: {filenames}")
        
        file_info = store.get_file_info()
        print(f"✅ File info: {file_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload store test failed: {e}")
        return False


def test_analytics_service():
    """Test the analytics service with uploaded data"""
    print("\n🔍 Testing Analytics Service...")
    
    try:
        from file_upload_fix import FixedAnalyticsService
        
        service = FixedAnalyticsService()
        
        health = service.health_check()
        print(f"✅ Service health: {health}")
        
        results = service.get_analytics_by_source("uploaded")
        print(f"✅ Analytics results: {results.get('status')} - {results.get('total_events', 0)} events")
        
        return results.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Analytics service test failed: {e}")
        return False


def test_column_mapping():
    """Test automatic column mapping"""
    print("\n🗂️ Testing Column Mapping...")
    
    try:
        from file_upload_fix import FixedAnalyticsService
        
        service = FixedAnalyticsService()
        
        test_data = {
            'Event Time': ['2024-01-01 10:00:00', '2024-01-01 10:15:00'],
            'User ID': ['USER001', 'USER002'],
            'Door Location': ['MAIN_ENTRANCE', 'SERVER_ROOM'],
            'Access Status': ['Granted', 'Denied']
        }
        
        df = pd.DataFrame(test_data)
        mapped_df = service._auto_map_columns(df)
        
        if mapped_df is not None:
            print("✅ Column mapping successful")
            print(f"   Mapped columns: {list(mapped_df.columns)}")
            return True
        else:
            print("❌ Column mapping failed")
            return False
            
    except Exception as e:
        print(f"❌ Column mapping test failed: {e}")
        return False


def run_diagnostic_check():
    """Run comprehensive diagnostic check"""
    print("🔧 UPLOAD SYSTEM DIAGNOSTIC CHECK")
    print("=" * 50)
    
    print("\n1️⃣ Creating test files...")
    try:
        test_files = save_test_files()
        print("✅ Test file creation: PASSED")
        df = test_files['dataframe']
        print(f"   Sample data: {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    except Exception as e:
        print(f"❌ Test file creation: FAILED - {e}")
        return False
    
    print("\n2️⃣ Testing upload store...")
    store_success = test_upload_store()
    if store_success:
        print("✅ Upload store: PASSED")
    else:
        print("❌ Upload store: FAILED")
    
    print("\n3️⃣ Testing analytics service...")
    analytics_success = test_analytics_service()
    if analytics_success:
        print("✅ Analytics service: PASSED")
    else:
        print("❌ Analytics service: FAILED")
    
    print("\n4️⃣ Testing column mapping...")
    mapping_success = test_column_mapping()
    if mapping_success:
        print("✅ Column mapping: PASSED")
    else:
        print("❌ Column mapping: FAILED")
    
    print("\n" + "=" * 50)
    all_passed = store_success and analytics_success and mapping_success
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Upload system should work correctly.")
        print("\nNext steps:")
        print("1. Apply the fixes to your actual files")
        print("2. Restart your Dash application")
        print("3. Upload the test files generated in temp/test_files/")
        print("4. Check that files appear in analytics dropdown")
    else:
        print("❌ SOME TESTS FAILED. Review the errors above.")
        print("\nTroubleshooting:")
        print("1. Ensure all required imports are available")
        print("2. Check file permissions in temp/ directory")
        print("3. Verify the fix files are properly integrated")
    
    return all_passed


def create_manual_test_instructions():
    """Create manual testing instructions"""
    instructions = """
🔧 MANUAL TESTING INSTRUCTIONS
==============================

STEP 1: Apply the fixes from file_upload_fix.py to your actual files

STEP 2: Test file upload in browser
    1. Navigate to /file-upload page
    2. Upload the test CSV file from temp/test_files/test_access_data.csv
    3. Verify you see success message with file details
    4. Check that file preview shows correct data

STEP 3: Test analytics integration
    1. Navigate to /analytics page
    2. In data source dropdown, select "uploaded"
    3. Verify you can see the uploaded file mentioned
    4. Select analysis type (e.g., "security")
    5. Click "Generate Analytics"
    6. Verify analytics run successfully with your uploaded data

STEP 4: Test persistence
    1. Refresh the browser page
    2. Check that uploaded files are still available
    3. Verify analytics still work with persisted data

EXPECTED RESULTS:
✅ Files upload successfully and show in UI
✅ Uploaded files appear as available data source
✅ Analytics run without "no data" errors
✅ File data persists across page refreshes
✅ Error messages are clear and helpful

COMMON ISSUES:
❌ "No uploaded data found" → Check file upload integration
❌ "Missing required columns" → Verify column mapping
❌ Analytics shows 0 events → Check data retrieval functions
❌ Files disappear on refresh → Check persistence system
"""
    
    instructions_path = Path("temp/test_instructions.txt")
    instructions_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(instructions_path, 'w') as f:
        f.write(instructions)
    
    print(f"📄 Manual test instructions saved to: {instructions_path}")
    return instructions


if __name__ == "__main__":
    print("🚀 Starting Upload System Tests...")
    
    success = run_diagnostic_check()
    
    print("\n📋 Creating manual test instructions...")
    instructions = create_manual_test_instructions()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DIAGNOSTIC COMPLETE - System appears ready!")
        print("📁 Test files created in: temp/test_files/")
        print("📄 Instructions available in: temp/test_instructions.txt")
    else:
        print("⚠️ DIAGNOSTIC COMPLETE - Issues detected!")
        print("Please review the errors above before proceeding.")
    
    print("\nFor immediate testing:")
    print("1. Apply the fixes from file_upload_fix.py")
    print("2. Restart your Dash app")
    print("3. Upload temp/test_files/test_access_data.csv")
    print("4. Try running analytics on uploaded data")
