# quick_test.py
import pandas as pd

csv_file = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"

try:
    from services.file_processor import FileProcessor
    
    processor = FileProcessor(upload_folder="temp", allowed_extensions={'csv', 'json', 'xlsx'})
    
    df = pd.read_csv(csv_file)
    print(f"Testing with {len(df)} rows...")
    
    result = processor._validate_data(df)
    
    if result['valid']:
        processed_df = result.get('data', df)
        print(f"SUCCESS: {len(processed_df)} records processed!")
        print(f"Your dashboard should now show {len(processed_df)} events!")
    else:
        print(f"Still failing: {result.get('error')}")
        
except Exception as e:
    print(f"Error: {e}")