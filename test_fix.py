#!/usr/bin/env python3
"""Test the analytics fix"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from data_diagnostics import fix_zero_actives_issue

# Test with sample data that mimics your structure
test_data = pd.DataFrame({
    'user_name': ['John', 'Jane', 'Bob'] * 100,  # 300 rows
    'access_location': ['Door A', 'Door B', 'Door C'] * 100,
    'result': ['Success', 'Failed', 'Success'] * 100,
    'event_time': pd.date_range('2025-06-24', periods=300, freq='5min')
})

print("🧪 Testing fix with sample data...")
results = fix_zero_actives_issue(test_data)

print(f"✅ Results:")
print(f"   Total Events: {results['total_events']}")
print(f"   Active Users: {results['active_users']}")
print(f"   Active Doors: {results['active_doors']}")

if results['active_users'] > 0 and results['active_doors'] > 0:
    print("🎉 FIX WORKING! Your analytics should now show correct counts.")
else:
    print("❌ Still issues - check your data structure")