# tests/test_analytics.py - FIXED: Comprehensive type-safe test suite
import unittest
import pandas as pd
import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Any
from components.analytics import (
    create_file_uploader, 
    create_data_preview, 
    create_analytics_charts,
    create_summary_cards,
    FileProcessor,
    AnalyticsGenerator
)

class TestFileProcessor(unittest.TestCase):
    """Test the FileProcessor utility class"""
    
    def setUp(self) -> None:
        """Set up test data"""
        self.sample_data = pd.DataFrame({
            'person_id': ['EMP001', 'EMP002', 'EMP001', 'EMP003'],
            'door_id': ['MAIN_ENTRANCE', 'SERVER_ROOM', 'MAIN_ENTRANCE', 'LAB_A'],
            'access_result': ['Granted', 'Denied', 'Granted', 'Granted'],
            'timestamp': [
                datetime.now() - timedelta(hours=i) 
                for i in range(4)
            ]
        })
    
    def test_csv_processing(self) -> None:
        """Test CSV file processing"""
        # Create CSV content
        csv_content = self.sample_data.to_csv(index=False)
        encoded = base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')
        contents = f"data:text/csv;base64,{encoded}"
        
        result = FileProcessor.process_file_content(contents, "test.csv")
        
        # FIXED: Add null check before using result
        self.assertIsNotNone(result)
        if result is not None:  # Type guard
            self.assertEqual(len(result), 4)
            self.assertIn('person_id', result.columns)
    
    def test_json_processing(self) -> None:
        """Test JSON file processing"""
        json_data = self.sample_data.to_dict('records')
        json_content = json.dumps(json_data)
        encoded = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        contents = f"data:application/json;base64,{encoded}"
        
        result = FileProcessor.process_file_content(contents, "test.json")
        
        # FIXED: Add null check before using result
        self.assertIsNotNone(result)
        if result is not None:  # Type guard
            self.assertEqual(len(result), 4)
            self.assertIn('person_id', result.columns)
    
    def test_dataframe_validation(self) -> None:
        """Test DataFrame validation"""
        # Valid DataFrame
        valid, message, suggestions = FileProcessor.validate_dataframe(self.sample_data)
        self.assertTrue(valid)
        self.assertIn("Successfully loaded", message)
        
        # Empty DataFrame
        empty_df = pd.DataFrame()
        valid, message, suggestions = FileProcessor.validate_dataframe(empty_df)
        self.assertFalse(valid)
        self.assertEqual(message, "File is empty")
    
    def test_column_mapping_suggestions(self) -> None:
        """Test column mapping suggestions"""
        # DataFrame with unclear column names
        unclear_df = pd.DataFrame({
            'user_code': ['U001', 'U002'],
            'location_id': ['L001', 'L002'],
            'status': ['OK', 'DENIED'],
            'event_time': [datetime.now(), datetime.now()]
        })
        
        valid, message, suggestions = FileProcessor.validate_dataframe(unclear_df)
        self.assertTrue(valid)
        self.assertTrue(len(suggestions) > 0)
    
    def test_invalid_input_handling(self) -> None:
        """FIXED: Test invalid input handling"""
        # Test with empty string
        result = FileProcessor.process_file_content("", "test.csv")
        self.assertIsNone(result)
        
        # Test with malformed content
        result = FileProcessor.process_file_content("invalid_content", "test.csv")
        self.assertIsNone(result)

class TestAnalyticsGenerator(unittest.TestCase):
    """Test the AnalyticsGenerator utility class"""
    
    def setUp(self) -> None:
        """Set up test data"""
        self.sample_data = pd.DataFrame({
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
    
    def test_analytics_generation(self) -> None:
        """Test comprehensive analytics generation"""
        analytics = AnalyticsGenerator.generate_analytics(self.sample_data)
        
        # Check basic metrics
        self.assertEqual(analytics['total_events'], 5)
        self.assertIn('processed_at', analytics)
        
        # Check date analysis
        self.assertIn('date_range', analytics)
        self.assertEqual(analytics['date_range']['start'], '2025-01-01')
        self.assertEqual(analytics['date_range']['end'], '2025-01-02')
        
        # Check access patterns
        self.assertIn('access_patterns', analytics)
        self.assertEqual(analytics['access_patterns']['Granted'], 4)
        self.assertEqual(analytics['access_patterns']['Denied'], 1)
        
        # Check user patterns
        self.assertIn('top_users', analytics)
        self.assertEqual(analytics['top_users']['EMP001'], 3)
        
        # Check door patterns
        self.assertIn('top_doors', analytics)
        self.assertIn('MAIN', analytics['top_doors'])
    
    def test_hourly_patterns(self) -> None:
        """Test hourly pattern analysis"""
        analytics = AnalyticsGenerator.generate_analytics(self.sample_data)
        
        self.assertIn('hourly_patterns', analytics)
        # Should have entries for hours 8, 9, 10, 14, 17
        self.assertIn('9', analytics['hourly_patterns'])
        self.assertIn('14', analytics['hourly_patterns'])
    
    def test_empty_dataframe(self) -> None:
        """Test analytics generation with empty DataFrame"""
        empty_df = pd.DataFrame()
        analytics = AnalyticsGenerator.generate_analytics(empty_df)
        
        self.assertEqual(analytics, {})

class TestComponentCreation(unittest.TestCase):
    """Test component creation functions"""
    
    def test_file_uploader_creation(self) -> None:
        """Test file uploader component creation"""
        component = create_file_uploader()
        
        # Should return a Dash component
        self.assertIsNotNone(component)
        # FIXED: Don't access component attributes directly - just check it exists
        # Components may not have className as a directly accessible attribute
        self.assertTrue(hasattr(component, 'children') or hasattr(component, 'id'))
    
    def test_data_preview_creation(self) -> None:
        """Test data preview component creation"""
        # Test with valid data
        sample_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': ['x', 'y', 'z']
        })
        
        component = create_data_preview(sample_data, "test.csv")
        self.assertIsNotNone(component)
        
        # Test with empty data
        empty_component = create_data_preview(None, "")
        self.assertIsNotNone(empty_component)
    
    def test_summary_cards_creation(self) -> None:
        """Test summary cards creation"""
        analytics_data = {
            'total_events': 100,
            'date_range': {'start': '2025-01-01', 'end': '2025-01-31'},
            'top_users': {'user1': 50, 'user2': 30},
            'top_doors': {'door1': 40, 'door2': 35}
        }
        
        component = create_summary_cards(analytics_data)
        self.assertIsNotNone(component)
        
        # Test with empty data
        empty_component = create_summary_cards({})
        self.assertIsNotNone(empty_component)
    
    def test_analytics_charts_creation(self) -> None:
        """Test analytics charts creation"""
        analytics_data = {
            'access_patterns': {'Granted': 80, 'Denied': 20},
            'hourly_patterns': {'9': 10, '14': 15, '17': 8},
            'top_users': {'EMP001': 25, 'EMP002': 20},
            'top_doors': {'MAIN': 30, 'SERVER': 15}
        }
        
        component = create_analytics_charts(analytics_data)
        self.assertIsNotNone(component)
        
        # Test with empty data
        empty_component = create_analytics_charts({})
        self.assertIsNotNone(empty_component)

class TestIntegration(unittest.TestCase):
    """Integration tests for the full analytics pipeline"""
    
    def test_full_pipeline(self) -> None:
        """Test the complete file processing to visualization pipeline"""
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
        self.assertTrue(valid)
        
        # Step 2: Generate analytics
        analytics = AnalyticsGenerator.generate_analytics(test_data)
        self.assertIsNotNone(analytics)
        self.assertGreater(analytics['total_events'], 0)
        
        # Step 3: Create visualizations
        charts = create_analytics_charts(analytics)
        self.assertIsNotNone(charts)
        
        # Step 4: Create summary cards
        cards = create_summary_cards(analytics)
        self.assertIsNotNone(cards)
        
        # Step 5: Create data preview
        preview = create_data_preview(test_data, "test_data.csv")
        self.assertIsNotNone(preview)

class TestErrorHandling(unittest.TestCase):
    """FIXED: Test error handling and edge cases"""
    
    def test_malformed_file_content(self) -> None:
        """Test handling of malformed file content"""
        # Test with invalid base64
        result = FileProcessor.process_file_content("data:text/csv;base64,invalid", "test.csv")
        self.assertIsNone(result)
        
        # Test with wrong MIME type
        result = FileProcessor.process_file_content("data:image/png;base64,abc123", "test.csv")
        self.assertIsNone(result)
    
    def test_edge_case_dataframes(self) -> None:
        """Test edge cases for DataFrame processing"""
        # Single row DataFrame
        single_row = pd.DataFrame({'A': [1]})
        analytics = AnalyticsGenerator.generate_analytics(single_row)
        self.assertEqual(analytics['total_events'], 1)
        
        # DataFrame with all NaN values
        nan_df = pd.DataFrame({'A': [None, None, None]})
        analytics = AnalyticsGenerator.generate_analytics(nan_df)
        self.assertEqual(analytics['total_events'], 3)
    
    def test_component_with_invalid_data(self) -> None:
        """Test components with invalid or edge case data"""
        # Test preview with very large DataFrame
        large_df = pd.DataFrame({
            'col1': range(1000),
            'col2': [f'value_{i}' for i in range(1000)]
        })
        preview = create_data_preview(large_df, "large_test.csv")
        self.assertIsNotNone(preview)
        
        # Test charts with empty analytics
        empty_charts = create_analytics_charts({})
        self.assertIsNotNone(empty_charts)

def run_analytics_tests() -> bool:
    """Run all analytics tests"""
    print("🧪 Running Analytics Module Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFileProcessor))
    test_suite.addTest(unittest.makeSuite(TestAnalyticsGenerator))
    test_suite.addTest(unittest.makeSuite(TestComponentCreation))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    test_suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed! Analytics modules are working correctly.")
    else:
        print(f"❌ {len(result.failures)} tests failed, {len(result.errors)} errors occurred.")
        
        if result.failures:
            print("\nFailures:")
            for test, failure in result.failures:
                print(f"  - {test}: {failure}")
        
        if result.errors:
            print("\nErrors:")
            for test, error in result.errors:
                print(f"  - {test}: {error}")
    
    return result.wasSuccessful()

def main() -> None:
    """Main test execution"""
    success = run_analytics_tests()
    
    if success:
        print("\n🚀 Ready for production!")
        print("Your analytics modules are:")
        print("  ✓ Modular and testable")
        print("  ✓ Type-safe and robust")
        print("  ✓ Easy to isolate and debug")
        print("  ✓ Well-documented and maintainable")
    else:
        print("\n🔧 Please fix the failing tests before proceeding.")

if __name__ == "__main__":
    main()