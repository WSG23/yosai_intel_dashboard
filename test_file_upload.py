
import pandas as pd
import base64

# Create test data
test_data = pd.DataFrame({
    'employee_id': ['E001', 'E002', 'E003'],
    'access_point': ['ENTRANCE', 'SERVER', 'EXIT'],
    'result': ['GRANTED', 'DENIED', 'GRANTED'],
    'timestamp': ['2025-01-01 09:00:00', '2025-01-01 14:30:00', '2025-01-01 17:45:00']
})

# Convert to CSV
csv_string = test_data.to_csv(index=False)

# Encode as base64 (like Dash does)
encoded = base64.b64encode(csv_string.encode('utf-8')).decode('utf-8')
contents = f"data:text/csv;base64,{encoded}"

print("Test upload contents:")
print(f"Length: {len(contents)}")
print(f"First 100 chars: {contents[:100]}")

# Test file processing
try:
    from components.analytics.file_processing import FileProcessor
    result = FileProcessor.process_file_content(contents, "test.csv")
    if result is not None:
        print(f"✅ Processing successful: {len(result)} rows")
        print(f"Columns: {list(result.columns)}")
    else:
        print("❌ Processing failed")
except Exception as e:
    print(f"❌ Error: {e}")
