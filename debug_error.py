#!/usr/bin/env python3
"""
Debug the actual error in your file processor
Run this to see the real error that's being hidden
"""

import pandas as pd
import os
import sys
from typing import Dict, Any, Sequence

# Add current directory to path
sys.path.append('.')

def debug_current_processor():
    """Test your current file processor to see the actual error"""
    
    # Your file path
    csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"
    
    print("🔍 DEBUGGING YOUR CURRENT FILE PROCESSOR")
    print("=" * 50)
    
    # Test direct pandas read first
    try:
        print("📊 1. Testing direct pandas read...")
        df = pd.read_csv(csv_file)
        print(f"   ✅ File loads: {len(df)} rows, {len(df.columns)} columns")
        print(f"   📋 Columns: {list(df.columns)}")
        print(f"   📋 Sample data:")
        print(df.head(2).to_string())
    except Exception as e:
        print(f"   ❌ Direct read failed: {e}")
        return
    
    # Test fuzzy matching function
    print(f"\n🔧 2. Testing fuzzy matching...")
    
    # Simulate your current fuzzy matching
    available_columns = list(df.columns)
    required_columns = ['person_id', 'door_id', 'access_result', 'timestamp']
    
    mapping_patterns = {
        'person_id': ['user', 'employee', 'badge', 'card', 'id'],
        'door_id': ['door', 'reader', 'device', 'access_point'],
        'access_result': ['result', 'status', 'outcome', 'decision'],
        'timestamp': ['time', 'date', 'when', 'occurred']
    }
    
    # Current fuzzy matching logic
    current_suggestions = {}
    for required_col, patterns in mapping_patterns.items():
        for available_col in available_columns:
            for pattern in patterns:
                if pattern in available_col.lower():
                    current_suggestions[required_col] = available_col
                    break
            if required_col in current_suggestions:
                break
    
    print(f"   📋 Available columns: {available_columns}")
    print(f"   📋 Required columns: {required_columns}")
    print(f"   🔧 Current fuzzy matches: {current_suggestions}")
    print(f"   📊 Missing mappings: {[col for col in required_columns if col not in current_suggestions]}")
    
    # Show why current matching fails
    print(f"\n❌ 3. Why current matching fails:")
    for required_col in required_columns:
        if required_col not in current_suggestions:
            print(f"   Missing: {required_col}")
            print(f"   Looking for patterns: {mapping_patterns[required_col]}")
            print(f"   In columns: {[col for col in available_columns if any(pattern in col.lower() for pattern in mapping_patterns[required_col])]}")
    
    # Test improved fuzzy matching
    print(f"\n✅ 4. Testing improved fuzzy matching...")
    
    # Enhanced patterns that match your data
    enhanced_patterns = {
        'person_id': [
            'person id', 'userid', 'user id', 'person_id',
            'user', 'employee', 'badge', 'card', 'person'
        ],
        'door_id': [
            'device name', 'devicename', 'device_name', 'door_id',
            'door', 'reader', 'device', 'access_point', 'gate'
        ],
        'access_result': [
            'access result', 'accessresult', 'access_result',
            'result', 'status', 'outcome', 'decision'
        ],
        'timestamp': [
            'timestamp', 'time', 'datetime', 'date',
            'when', 'occurred', 'event_time'
        ]
    }
    
    enhanced_suggestions = {}
    available_lower = {col.lower(): col for col in available_columns}
    
    for required_col, patterns in enhanced_patterns.items():
        for pattern in patterns:
            if pattern.lower() in available_lower:
                enhanced_suggestions[required_col] = available_lower[pattern.lower()]
                break
    
    print(f"   🔧 Enhanced fuzzy matches: {enhanced_suggestions}")
    print(f"   📊 Missing mappings: {[col for col in required_columns if col not in enhanced_suggestions]}")
    
    # Test column mapping
    if len(enhanced_suggestions) == len(required_columns):
        print(f"\n✅ 5. Testing column mapping...")
        try:
            df_mapped = df.rename(columns=enhanced_suggestions)
            print(f"   ✅ Mapping successful!")
            print(f"   📋 New columns: {list(df_mapped.columns)}")
            
            # Test access result standardization
            if 'access_result' in df_mapped.columns:
                original_values = df_mapped['access_result'].unique()
                print(f"   📋 Original access results: {original_values}")
                
                # Standardize
                df_mapped['access_result'] = df_mapped['access_result'].str.replace('Access ', '', regex=False)
                standardized_values = df_mapped['access_result'].unique()
                print(f"   📋 Standardized access results: {standardized_values}")
            
            print(f"   🎯 FINAL RESULT: {len(df_mapped)} records ready for processing!")
            
        except Exception as e:
            print(f"   ❌ Mapping failed: {e}")
    else:
        print(f"\n❌ 5. Cannot map all columns")
    
    # Test your actual file processor if available
    print(f"\n🔧 6. Testing your actual file processor...")
    try:
        # Try to import and test your actual processor
        from services.file_processor import FileProcessor
        
        processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})
        
        # Read the file and test validation
        test_df = pd.read_csv(csv_file)
        validation_result = processor._validate_data(test_df)
        
        print(f"   📋 Validation result: {validation_result}")
        
        if not validation_result.get('valid', False):
            print(f"   ❌ Validation failed: {validation_result.get('error', 'Unknown error')}")
            if 'suggestions' in validation_result:
                print(f"   🔧 Suggestions: {validation_result['suggestions']}")
        else:
            print(f"   ✅ Validation passed!")
            
    except Exception as e:
        print(f"   ❌ Processor test failed: {e}")
        import traceback
        print(f"   📋 Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_current_processor()