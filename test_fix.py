from file_processor_fix import test_file_processing

# Test your uploaded files
test_files = [
    'uploads/your_file1.csv',
    'uploads/your_file2.xlsx'
]

for file_path in test_files:
    print(f"\n{'='*50}")
    print(f"TESTING: {file_path}")
    print('='*50)

    result = test_file_processing(file_path)

    if result['total_events'] > 0:
        print("\u2705 SUCCESS: File processed correctly")
    else:
        print("\u274C FAILED: Still getting 0 records")
        print("Check the error messages above")
