# test_column_fix.py
import pandas as pd
from services.file_processor import FileProcessor

# Test with a small sample
csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"

processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})

# Test first few rows
df = pd.read_csv(csv_file, nrows=10)
print(f"Original columns: {list(df.columns)}")

result = processor._validate_data(df)

if result['valid']:
    processed_df = result['data']
    print(f"Final columns: {list(processed_df.columns)}")
    print(f"Has person_id: {'person_id' in processed_df.columns}")
    print(f"Has door_id: {'door_id' in processed_df.columns}")
    print(f"Has timestamp: {'timestamp' in processed_df.columns}")
    print(f"Sample data:")
    print(processed_df[['person_id', 'door_id', 'access_result', 'timestamp']].head(2))
else:
    print(f"Validation failed: {result}")