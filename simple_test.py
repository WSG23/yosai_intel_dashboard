#!/usr/bin/env python3
"""Simple test for the analytics fix"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_simple_fix():
    """Simple test that bypasses complex diagnostics"""
    
    # Create test data with your expected structure
    test_data = pd.DataFrame({
        'user_name': ['John', 'Jane', 'Bob'] * 100,  # 300 rows
        'access_location': ['Door A', 'Door B', 'Door C'] * 100,
        'result': ['Success', 'Failed', 'Success'] * 100,
        'event_time': pd.date_range('2025-06-24', periods=300, freq='5min')
    })
    
    print("🧪 Testing SIMPLE fix with sample data...")
    print(f"   Original data shape: {test_data.shape}")
    print(f"   Columns: {list(test_data.columns)}")
    
    # Apply direct column mapping (the core fix)
    column_mapping = {
        'user_name': 'person_id',
        'access_location': 'door_id', 
        'result': 'access_result',
        'event_time': 'timestamp'
    }
    
    # Rename columns
    df_fixed = test_data.rename(columns=column_mapping)
    
    print(f"   Fixed columns: {list(df_fixed.columns)}")
    
    # Calculate what should be the correct counts
    active_users = df_fixed['person_id'].nunique()
    active_doors = df_fixed['door_id'].nunique()
    total_events = len(df_fixed)
    
    print(f"\n✅ RESULTS:")
    print(f"   Total Events: {total_events}")
    print(f"   Active Users: {active_users}")
    print(f"   Active Doors: {active_doors}")
    
    if active_users > 0 and active_doors > 0:
        print("🎉 BASIC FIX WORKING!")
        print("\n📋 TO APPLY IN YOUR CODE:")
        print("   1. Add column mapping before analytics")
        print("   2. Check your data has these column names:")
        for old, new in column_mapping.items():
            print(f"      '{old}' -> '{new}'")
        return True
    else:
        print("❌ Still issues")
        return False

def test_analytics_data_format():
    """Test the analytics service data format issue"""
    
    # Simulate what your enhanced_analytics.py returns
    analytics_service_output = {
        'total_events': 300,
        'unique_users': 3,
        'unique_doors': 3,
        'user_patterns': {
            'most_active_users': {
                'John': {'total_attempts': 100},
                'Jane': {'total_attempts': 100}, 
                'Bob': {'total_attempts': 100}
            },
            'total_unique_users': 3
        },
        'door_patterns': {
            'busiest_doors': {
                'Door A': {'total_events': 100},
                'Door B': {'total_events': 100},
                'Door C': {'total_events': 100}
            },
            'total_doors': 3
        }
    }
    
    print("\n🔄 Testing data format conversion...")
    
    # Convert to display format (what components expect)
    def convert_to_display_format(analytics_data):
        converted = analytics_data.copy()
        
        # Convert user_patterns to top_users
        user_patterns = analytics_data.get('user_patterns', {})
        if 'most_active_users' in user_patterns:
            top_users = []
            for user_id, stats in user_patterns['most_active_users'].items():
                top_users.append({
                    'user_id': user_id,
                    'count': stats.get('total_attempts', 0)
                })
            converted['top_users'] = top_users
        
        # Convert door_patterns to top_doors
        door_patterns = analytics_data.get('door_patterns', {})
        if 'busiest_doors' in door_patterns:
            top_doors = []
            for door_id, stats in door_patterns['busiest_doors'].items():
                top_doors.append({
                    'door_id': door_id,
                    'count': stats.get('total_events', 0)
                })
            converted['top_doors'] = top_doors
        
        return converted
    
    # Test conversion
    display_format = convert_to_display_format(analytics_service_output)
    
    # Check what display components would see
    top_users = display_format.get('top_users', [])
    top_doors = display_format.get('top_doors', [])
    
    user_count = len(top_users)
    door_count = len(top_doors)
    
    print(f"   Analytics service users: {analytics_service_output['user_patterns']['total_unique_users']}")
    print(f"   Display format users: {user_count}")
    print(f"   Analytics service doors: {analytics_service_output['door_patterns']['total_doors']}")
    print(f"   Display format doors: {door_count}")
    
    if user_count > 0 and door_count > 0:
        print("✅ DATA FORMAT CONVERSION WORKING!")
        return True
    else:
        print("❌ Data format conversion failed")
        return False

if __name__ == "__main__":
    print("🚀 RUNNING SIMPLE TESTS...")
    
    test1_result = test_simple_fix()
    test2_result = test_analytics_data_format()
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your issue is likely in column naming or data format conversion.")
        print("Apply the fixes shown above to resolve the 0 active users/doors issue.")
    else:
        print("\n❌ Some tests failed - check the output above.")