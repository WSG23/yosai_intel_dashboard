#!/usr/bin/env python3
"""
Simple test script - no imports needed
Save as simple_test.py and run: python3 simple_test.py
"""

import pandas as pd
import json
import os

# Your file paths
csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"
json_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/key_fob_access_log_sample.json"

def test_csv_file():
    """Test the CSV file"""
    print("🔍 TESTING CSV FILE")
    print("=" * 30)
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return 0
    
    try:
        # Load the CSV
        df = pd.read_csv(csv_file)
        print(f"✅ File loaded successfully")
        print(f"📊 Total rows: {len(df)}")
        print(f"📊 Total columns: {len(df.columns)}")
        print(f"📊 Column names: {list(df.columns)}")
        
        # Show sample data
        print(f"\n📋 Sample data (first 3 rows):")
        print(df.head(3).to_string())
        
        # Look for access control related columns
        potential_mappings = {}
        columns_lower = [col.lower() for col in df.columns]
        
        # Check for person/user columns
        person_keywords = ['person', 'user', 'employee', 'badge', 'card', 'id']
        for keyword in person_keywords:
            for i, col in enumerate(columns_lower):
                if keyword in col:
                    potential_mappings['person_id'] = df.columns[i]
                    break
            if 'person_id' in potential_mappings:
                break
        
        # Check for door/device columns  
        door_keywords = ['door', 'reader', 'device', 'access', 'gate', 'entry']
        for keyword in door_keywords:
            for i, col in enumerate(columns_lower):
                if keyword in col:
                    potential_mappings['door_id'] = df.columns[i]
                    break
            if 'door_id' in potential_mappings:
                break
        
        # Check for result/status columns
        result_keywords = ['result', 'status', 'outcome', 'success', 'granted', 'denied']
        for keyword in result_keywords:
            for i, col in enumerate(columns_lower):
                if keyword in col:
                    potential_mappings['access_result'] = df.columns[i]
                    break
            if 'access_result' in potential_mappings:
                break
        
        # Check for timestamp columns
        time_keywords = ['time', 'date', 'when', 'occurred', 'stamp']
        for keyword in time_keywords:
            for i, col in enumerate(columns_lower):
                if keyword in col:
                    potential_mappings['timestamp'] = df.columns[i]
                    break
            if 'timestamp' in potential_mappings:
                break
        
        print(f"\n🔧 Suggested column mappings:")
        for target, source in potential_mappings.items():
            print(f"   {target} ← {source}")
        
        return len(df)
        
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return 0

def test_json_file():
    """Test the JSON file"""
    print("\n🔍 TESTING JSON FILE")
    print("=" * 30)
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return 0
    
    try:
        # Load the JSON
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"✅ File loaded successfully")
        
        if isinstance(data, list):
            print(f"📊 Total records: {len(data)}")
            if len(data) > 0:
                df = pd.DataFrame(data)
                print(f"📊 Total columns: {len(df.columns)}")
                print(f"📊 Column names: {list(df.columns)}")
                
                # Show sample data
                print(f"\n📋 Sample data (first 3 rows):")
                print(df.head(3).to_string())
                
                return len(data)
            else:
                print("❌ JSON array is empty")
                return 0
        elif isinstance(data, dict):
            print(f"📊 Single JSON object")
            print(f"📊 Keys: {list(data.keys())}")
            print(f"\n📋 Sample data:")
            for key, value in list(data.items())[:5]:  # Show first 5 key-value pairs
                print(f"   {key}: {value}")
            return 1
        else:
            print(f"❌ Unexpected JSON format: {type(data)}")
            return 0
            
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return 0

def main():
    print("🚀 SIMPLE FILE TEST")
    print("=" * 50)
    
    csv_records = test_csv_file()
    json_records = test_json_file()
    
    print(f"\n📊 SUMMARY")
    print("=" * 20)
    print(f"CSV records:  {csv_records}")
    print(f"JSON records: {json_records}")
    print(f"TOTAL:        {csv_records + json_records}")
    
    if csv_records + json_records > 0:
        print(f"\n✅ SUCCESS: Found {csv_records + json_records} total records!")
        print(f"Your files contain data and can be processed.")
    else:
        print(f"\n❌ No records found in either file.")

if __name__ == "__main__":
    main()