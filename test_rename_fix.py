# test_rename_fix.py
import pandas as pd

# Test data
data = {
    'Timestamp': ['2023-03-22 01:14:16.000'],
    'Person ID': ['P430404'],
    'Device name': ['F01C Staircase C'],
    'Access result': ['Access Granted']
}

df = pd.DataFrame(data)
print(f"Original columns: {list(df.columns)}")

# Test current fuzzy matches (wrong direction)
fuzzy_matches = {'person_id': 'Person ID', 'door_id': 'Device name', 'access_result': 'Access result', 'timestamp': 'Timestamp'}
print(f"Fuzzy matches: {fuzzy_matches}")

# This doesn't work (current approach)
df_wrong = df.rename(columns=fuzzy_matches)
print(f"Wrong rename result: {list(df_wrong.columns)}")

# This works (fixed approach)
rename_dict = {source_col: target_col for target_col, source_col in fuzzy_matches.items()}
df_correct = df.rename(columns=rename_dict)
print(f"Correct rename dict: {rename_dict}")
print(f"Correct rename result: {list(df_correct.columns)}")