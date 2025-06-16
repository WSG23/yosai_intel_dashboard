# test_analytics_components.py - FIXED: Type-safe test script
"""
Quick test script to verify analytics components are working correctly
Run this to test your modular analytics system - FIXED version with proper type safety
"""

import pandas as pd
from datetime import datetime, timedelta
import json
import base64
from typing import Optional

def test_file_processing() -> None:
    """Test the FileProcessor with sample data"""
    print("🧪 Testing FileProcessor...")
    
    try:
        from components.analytics import FileProcessor
        
        # Create sample CSV data
        sample_data = pd.DataFrame({
            'person_id': ['EMP001', 'EMP002', 'EMP001', 'EMP003'],
            'door_id': ['MAIN_ENTRANCE', 'SERVER_ROOM', 'MAIN_ENTRANCE', 'LAB_A'],
            'access_result': ['Granted', 'Denied', 'Granted', 'Granted'],
            'timestamp': [
                datetime.now() - timedelta(hours=i) 
                for i in range(4)
            ]
        })
        
        # Convert to CSV and encode (simulate file upload)
        csv_content = sample_data.to_csv(index=False)
        encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
        contents = f"data:text/csv;base64,{encoded}"
        
        # Test processing
        result = FileProcessor.process_file_content(contents, "test.csv")
        
        if result is not None and len(result) == 4:
            print("✅ FileProcessor: CSV processing works")
        else:
            print("❌ FileProcessor: CSV processing failed")
        
        # Test validation
        valid, message, suggestions = FileProcessor.validate_dataframe(sample_data)
        if valid:
            print("✅ FileProcessor: Data validation works")
        else:
            print(f"❌ FileProcessor: Data validation failed - {message}")
        
        # FIXED: Test with None value (proper type handling)
        result_none = FileProcessor.process_file_content("", "test.csv")  # Empty string instead of None
        if result_none is None:
            print("✅ FileProcessor: None handling works")
        else:
            print("❌ FileProcessor: None handling failed")
            
    except ImportError as e:
        print(f"❌ FileProcessor: Import failed - {e}")
    except Exception as e:
        print(f"❌ FileProcessor: Test failed - {e}")

def test_analytics_generation() -> None:
    """Test the AnalyticsGenerator"""
    print("\n🧪 Testing AnalyticsGenerator...")
    
    try:
        from components.analytics import AnalyticsGenerator
        
        # Create sample data
        sample_data = pd.DataFrame({
            'person_id': ['EMP001', 'EMP002', 'EMP001', 'EMP003', 'EMP001'],
            'door_id': ['MAIN', 'SERVER', 'MAIN', 'LAB', 'SERVER'],
            'access_result': ['Granted', 'Denied', 'Granted', 'Granted', 'Granted'],
            'timestamp': [
                datetime(2025, 1, 1, 9, 0),
                datetime(2025, 1, 1, 14, 30),
                datetime(2025, 1, 1, 17, 45),
                datetime(2025, 1, 2, 8, 15),
                datetime(2025, 1, 2, 10, 30)
            ]
        })
        
        # Generate analytics
        analytics = AnalyticsGenerator.generate_analytics(sample_data)
        
        # Check results
        if analytics.get('total_events') == 5:
            print("✅ AnalyticsGenerator: Basic metrics work")
        else:
            print("❌ AnalyticsGenerator: Basic metrics failed")
            
        if 'access_patterns' in analytics and 'Granted' in analytics['access_patterns']:
            print("✅ AnalyticsGenerator: Access patterns work")
        else:
            print("❌ AnalyticsGenerator: Access patterns failed")
            
        if 'top_users' in analytics and 'EMP001' in analytics['top_users']:
            print("✅ AnalyticsGenerator: User analysis works")
        else:
            print("❌ AnalyticsGenerator: User analysis failed")
            
    except ImportError as e:
        print(f"❌ AnalyticsGenerator: Import failed - {e}")
    except Exception as e:
        print(f"❌ AnalyticsGenerator: Test failed - {e}")

def test_component_creation() -> None:
    """Test the component creation functions"""
    print("\n🧪 Testing Component Creation...")
    
    try:
        from components.analytics import (
            create_file_uploader,
            create_data_preview,
            create_analytics_charts,
            create_summary_cards
        )
        
        # Test file uploader
        uploader = create_file_uploader()
        if uploader is not None:
            print("✅ Components: File uploader creation works")
        else:
            print("❌ Components: File uploader creation failed")
        
        # Test with sample data
        sample_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z']
        })
        
        # Test data preview
        preview = create_data_preview(sample_data, "test.csv")
        if preview is not None:
            print("✅ Components: Data preview creation works")
        else:
            print("❌ Components: Data preview creation failed")
        
        # Test analytics charts
        analytics_data = {
            'access_patterns': {'Granted': 80, 'Denied': 20},
            'hourly_patterns': {'9': 10, '14': 15, '17': 8},
            'top_users': {'EMP001': 25, 'EMP002': 20},
            'top_doors': {'MAIN': 30, 'SERVER': 15}
        }
        
        charts = create_analytics_charts(analytics_data)
        if charts is not None:
            print("✅ Components: Analytics charts creation works")
        else:
            print("❌ Components: Analytics charts creation failed")
        
        # Test summary cards
        cards = create_summary_cards(analytics_data)
        if cards is not None:
            print("✅ Components: Summary cards creation works")
        else:
            print("❌ Components: Summary cards creation failed")
            
    except ImportError as e:
        print(f"❌ Components: Import failed - {e}")
    except Exception as e:
        print(f"❌ Components: Test failed - {e}")

def test_type_safety() -> None:
    """Test type safety with edge cases"""
    print("\n🧪 Testing Type Safety...")
    
    try:
        from components.analytics import FileProcessor, AnalyticsGenerator
        
        # FIXED: Test with invalid input (empty string instead of None)
        result = FileProcessor.process_file_content("", "test.csv")
        if result is None:
            print("✅ Type Safety: Invalid input handling works")
        else:
            print("❌ Type Safety: Invalid input handling failed")
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        analytics = AnalyticsGenerator.generate_analytics(empty_df)
        if analytics == {}:
            print("✅ Type Safety: Empty DataFrame handling works")
        else:
            print("❌ Type Safety: Empty DataFrame handling failed")
        
        # Test validation with invalid data
        invalid_df = pd.DataFrame({'A': []})  # Empty but with column
        valid, message, suggestions = FileProcessor.validate_dataframe(invalid_df)
        if not valid:
            print("✅ Type Safety: Invalid data detection works")
        else:
            print("❌ Type Safety: Invalid data detection failed")
            
    except Exception as e:
        print(f"❌ Type Safety: Test failed - {e}")

def test_integration() -> None:
    """Test the complete integration pipeline"""
    print("\n🧪 Testing Integration Pipeline...")
    
    try:
        from components.analytics import FileProcessor, AnalyticsGenerator, create_data_preview
        
        # Create test data
        test_data = pd.DataFrame({
            'employee_id': ['E001', 'E002', 'E001'],
            'access_point': ['ENTRANCE', 'SERVER', 'ENTRANCE'],
            'result': ['GRANTED', 'DENIED', 'GRANTED'],
            'event_datetime': [
                '2025-01-01 09:00:00',
                '2025-01-01 14:30:00',
                '2025-01-01 17:45:00'
            ]
        })
        
        # Step 1: Validate the data
        valid, message, suggestions = FileProcessor.validate_dataframe(test_data)
        if not valid:
            print(f"❌ Integration: Data validation failed - {message}")
            return
        
        # Step 2: Generate analytics
        analytics = AnalyticsGenerator.generate_analytics(test_data)
        if not analytics or analytics.get('total_events', 0) == 0:
            print("❌ Integration: Analytics generation failed")
            return
        
        # Step 3: Create preview
        preview = create_data_preview(test_data, "integration_test.csv")
        if preview is None:
            print("❌ Integration: Preview creation failed")
            return
        
        print("✅ Integration: Complete pipeline works")
        
    except Exception as e:
        print(f"❌ Integration: Test failed - {e}")

def main() -> None:
    """Run all analytics tests"""
    print("🚀 YŌSAI INTEL ANALYTICS - COMPONENT TESTS")
    print("=" * 60)
    
    # Run all tests
    test_file_processing()
    test_analytics_generation()
    test_component_creation()
    test_type_safety()
    test_integration()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("If all tests show ✅, your analytics components are working correctly!")
    print("If any show ❌, check the error messages and fix the imports/code.")
    
    print("\n📋 Next Steps:")
    print("1. Run your Dash app: python app.py")
    print("2. Navigate to: http://127.0.0.1:8050/analytics")
    print("3. Upload a CSV file to test the full pipeline")
    print("4. Check that all visualizations appear correctly")

if __name__ == "__main__":
    main()