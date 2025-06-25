from file_diagnosis import quick_diagnosis

file_paths = [
    'path/to/your/uploaded/file1.csv',
    'path/to/your/uploaded/file2.xlsx'
]

for file_path in file_paths:
    result = quick_diagnosis(file_path)
    print(f"File: {file_path}")
    print(f"Status: {result['status']}")
    if result['recommendations']:
        print("Fix needed:", result['recommendations'])
    print("-" * 50)
