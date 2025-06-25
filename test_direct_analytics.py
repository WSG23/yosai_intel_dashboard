# test_direct_analytics.py
#!/usr/bin/env python3
"""
Test analytics directly with your files (bypass upload system)
"""

def test_direct_analytics():
    print("🔍 TESTING DIRECT ANALYTICS (BYPASS UPLOAD)")
    print("=" * 50)
    
    # Your file paths
    csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"
    json_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/key_fob_access_log_sample.json"
    
    try:
        # Import what we need
        from services.file_processor import FileProcessor
        import pandas as pd
        import json
        import os
        
        # Check files exist
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        if not os.path.exists(json_file):
            print(f"❌ JSON file not found: {json_file}")
            return
            
        print(f"✅ Both files found")
        
        # Process files with your FIXED processor
        processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})
        
        all_data = []
        total_events = 0
        
        # Process CSV
        print(f"\n📊 Processing CSV file...")
        df_csv = pd.read_csv(csv_file)
        result_csv = processor._validate_data(df_csv)
        
        if result_csv['valid']:
            processed_csv = result_csv.get('data', df_csv)
            processed_csv['source_file'] = 'csv'
            all_data.append(processed_csv)
            total_events += len(processed_csv)
            print(f"   ✅ CSV: {len(processed_csv)} records")
        else:
            print(f"   ❌ CSV failed: {result_csv.get('error')}")
        
        # Process JSON
        print(f"\n📊 Processing JSON file...")
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        df_json = pd.DataFrame(json_data)
        result_json = processor._validate_data(df_json)
        
        if result_json['valid']:
            processed_json = result_json.get('data', df_json)
            processed_json['source_file'] = 'json'
            all_data.append(processed_json)
            total_events += len(processed_json)
            print(f"   ✅ JSON: {len(processed_json)} records")
        else:
            print(f"   ❌ JSON failed: {result_json.get('error')}")
        
        # Combine and generate analytics
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Calculate what your dashboard should show
            unique_users = combined_df['person_id'].nunique() if 'person_id' in combined_df.columns else 0
            unique_doors = combined_df['door_id'].nunique() if 'door_id' in combined_df.columns else 0
            
            print(f"\n🎯 FINAL ANALYTICS RESULTS:")
            print(f"   Total Events: {total_events}")
            print(f"   Active Users: {unique_users}")
            print(f"   Active Doors: {unique_doors}")
            print(f"   Date Range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
            
            # Show access results breakdown
            if 'access_result' in combined_df.columns:
                access_breakdown = combined_df['access_result'].value_counts()
                print(f"   Access Results: {access_breakdown.to_dict()}")
            
            print(f"\n✅ SUCCESS! This is what your dashboard should show!")
            return combined_df
            
        else:
            print(f"\n❌ No data could be processed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    test_direct_analytics()