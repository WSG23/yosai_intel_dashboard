# OPTION 1: Quick single file test
def quick_test():
    """Copy-paste this into your Python console"""
    
    # 1. Import the functions
    from file_diagnosis2 import quick_diagnosis
    from file_processor_fix import test_file_processing
    
    # 2. Replace with YOUR actual file path (or use one of the provided paths)
    file_path = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/Demo3_data.csv"  # ← CSV file
    # file_path = "/Users/tombrayman/Library/CloudStorage/Dropbox/1. YOSAI CODING/03_Data/Datasets/key_fob_access_log_sample.json"  # ← JSON file
    
    # 3. Run diagnosis
    print("🔍 DIAGNOSIS:")
    diagnosis_result = quick_diagnosis(file_path)
    
    # 4. Run processing  
    print("\n⚙️  PROCESSING:")
    processing_result = test_file_processing(file_path)
    
    # 5. Show results
    print(f"\n📊 FINAL RESULT:")
    print(f"Events found: {processing_result.get('total_events', 0)}")
    
    return processing_result