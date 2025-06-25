#!/usr/bin/env python3
"""
Test Analytics Integration
Run this to check if your analytics service is using the fixed processor
"""

def test_analytics_integration():
    """Test that analytics service uses the fixed processor"""
    
    print("🔍 TESTING ANALYTICS INTEGRATION")
    print("=" * 50)
    
    try:
        # Test the analytics service
        from services.analytics_service import get_analytics_service
        
        print("[INFO] Getting analytics service...")
        analytics_service = get_analytics_service()
        
        print("[INFO] Testing uploaded data source...")
        result = analytics_service.get_analytics_by_source("uploaded")
        
        print(f"[INFO] Analytics result status: {result.get('status', 'unknown')}")
        
        # Check the key metrics
        total_events = result.get('total_events', 0) or result.get('total_rows', 0)
        active_users = result.get('active_users', 0)
        active_doors = result.get('active_doors', 0)
        
        print(f"\n📊 DASHBOARD METRICS:")
        print(f"   Total Events: {total_events}")
        print(f"   Active Users: {active_users}")
        print(f"   Active Doors: {active_doors}")
        
        # Check for success
        if total_events > 0:
            print(f"\n✅ SUCCESS!")
            print(f"   Your dashboard should now show {total_events} events!")
            print(f"   Integration is working correctly.")
        else:
            print(f"\n❌ ISSUE DETECTED:")
            print(f"   Still getting 0 events from analytics service")
            print(f"   Result: {result}")
            
            # Debugging info
            if 'message' in result:
                print(f"   Message: {result['message']}")
            if 'processing_info' in result:
                print(f"   Processing info: {result['processing_info']}")
                
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        print(f"Full error:\n{traceback.format_exc()}")
        return None

def test_direct_file_processor():
    """Test the file processor directly as backup"""
    
    print(f"\n🔧 TESTING FILE PROCESSOR DIRECTLY")
    print("=" * 50)
    
    try:
        # Test your files directly
        csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"
        
        from services.file_processor import FileProcessor
        import pandas as pd
        
        processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})
        
        df = pd.read_csv(csv_file)
        result = processor._validate_data(df)
        
        if result['valid']:
            processed_df = result.get('data', df)
            print(f"✅ File processor working: {len(processed_df)} records")
            return True
        else:
            print(f"❌ File processor issue: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ File processor error: {e}")
        return False

if __name__ == "__main__":
    # Run both tests
    analytics_result = test_analytics_integration()
    processor_working = test_direct_file_processor()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 30)
    
    if analytics_result and analytics_result.get('total_events', 0) > 0:
        print("✅ Analytics integration: WORKING")
        print("🎉 Your dashboard should show the correct data!")
    else:
        print("❌ Analytics integration: NEEDS FIX")
        
        if processor_working:
            print("✅ File processor: WORKING")
            print("💡 Issue is in analytics service integration")
        else:
            print("❌ File processor: NEEDS FIX")
            print("💡 Apply the file processor fixes first")