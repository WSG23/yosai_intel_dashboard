"""
Test module for ColumnDataPresenter
Isolated testing for the column data presentation functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from column_data_presenter import ColumnDataPresenter, create_column_data_presenter


class TestColumnDataPresenter(unittest.TestCase):
    """Test cases for ColumnDataPresenter functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.presenter = ColumnDataPresenter(max_preview_rows=5)
        
        # Sample test data
        self.test_data = [
            {"timestamp": "2024-01-01 10:00:00", "device": "Door_A1", "user": "john_doe", "event": "granted"},
            {"timestamp": "2024-01-01 10:05:00", "device": "Door_B2", "user": "jane_smith", "event": "denied"},
            {"timestamp": "2024-01-01 10:10:00", "device": "Door_A1", "user": "bob_jones", "event": "granted"},
            {"timestamp": "2024-01-01 10:15:00", "device": "Door_C3", "user": None, "event": "error"},
            {"timestamp": "2024-01-01 10:20:00", "device": "Door_B2", "user": "alice_brown", "event": "granted"},
        ]
        
        self.test_mapping = {
            "timestamp": "timestamp",
            "device_name": "device", 
            "user_id": "user",
            "event_type": "event"
        }
    
    def test_presenter_initialization(self):
        """Test ColumnDataPresenter initializes correctly"""
        self.assertEqual(self.presenter.max_preview_rows, 5)
        self.assertIsInstance(self.presenter, ColumnDataPresenter)
    
    def test_factory_function(self):
        """Test factory function creates presenter correctly"""
        presenter = create_column_data_presenter(max_preview_rows=20)
        self.assertEqual(presenter.max_preview_rows, 20)
    
    def test_column_summary_creation(self):
        """Test column summary table creation"""
        result = self.presenter.create_column_summary_table(self.test_data, self.test_mapping)
        
        # Should return a Div component
        self.assertEqual(result.children[0].children, "📊 Column Mapping Summary")
        
        # Should contain a DataTable
        data_table = result.children[1]
        self.assertEqual(len(data_table.columns), 5)  # 5 summary columns
    
    def test_data_preview_creation(self):
        """Test data preview table creation"""
        result = self.presenter.create_data_preview_table(self.test_data, self.test_mapping)
        
        # Should return a Div component
        self.assertEqual(result.children[0].children, "🔍 Data Preview")
        
        # Should show preview info
        preview_info = result.children[1].children
        self.assertIn("Showing first", preview_info)
    
    def test_validation_status_creation(self):
        """Test validation status component creation"""
        result = self.presenter.create_validation_status(self.test_data, self.test_mapping)
        
        # Should return a Div component
        self.assertEqual(result.children[0].children, "🔎 Data Validation")
    
    def test_complete_presentation_generation(self):
        """Test complete presentation generation"""
        result = self.presenter.generate_complete_presentation(
            self.test_data, 
            self.test_mapping, 
            "test_file.csv"
        )
        
        # Should return a main container Div
        self.assertEqual(len(result.children), 5)  # Header, summary, validation, preview, buttons
        
        # Should contain header with filename
        header = result.children[0]
        self.assertIn("test_file.csv", str(header))
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        invalid_data = "not_a_list"
        
        result = self.presenter.create_column_summary_table(invalid_data, self.test_mapping)
        self.assertIn("Error creating column summary", str(result))
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = []
        
        result = self.presenter.create_data_preview_table(empty_data, self.test_mapping)
        # Should handle gracefully without crashing
        self.assertIsNotNone(result)
    
    def test_missing_columns_handling(self):
        """Test handling when mapped columns don't exist in data"""
        bad_mapping = {
            "timestamp": "nonexistent_column",
            "device_name": "also_nonexistent"
        }
        
        result = self.presenter.create_column_summary_table(self.test_data, bad_mapping)
        # Should handle gracefully without crashing
        self.assertIsNotNone(result)


class TestIntegrationScenarios(unittest.TestCase):
    """Test realistic integration scenarios"""
    
    def setUp(self):
        self.presenter = ColumnDataPresenter(max_preview_rows=10)
    
    def test_real_csv_scenario(self):
        """Test with realistic CSV data scenario"""
        csv_data = [
            {"Timestamp": "2024-01-01T10:00:00Z", "Door_ID": "MAIN_001", "Employee_ID": "EMP123", "Access_Result": "GRANTED"},
            {"Timestamp": "2024-01-01T10:05:00Z", "Door_ID": "SIDE_002", "Employee_ID": "EMP456", "Access_Result": "DENIED"},
            {"Timestamp": "2024-01-01T10:10:00Z", "Door_ID": "MAIN_001", "Employee_ID": "EMP789", "Access_Result": "GRANTED"},
        ]
        
        mapping = {
            "timestamp": "Timestamp",
            "device_name": "Door_ID",
            "user_id": "Employee_ID", 
            "event_type": "Access_Result"
        }
        
        result = self.presenter.generate_complete_presentation(csv_data, mapping, "access_log.csv")
        self.assertIsNotNone(result)
        self.assertIn("access_log.csv", str(result))
    
    def test_data_quality_issues(self):
        """Test detection of data quality issues"""
        poor_quality_data = [
            {"time": "2024-01-01", "device": "Door1", "user": "john", "event": "granted"},
            {"time": None, "device": "Door2", "user": None, "event": "denied"},
            {"time": "invalid_date", "device": None, "user": "jane", "event": None},
            {"time": "2024-01-02", "device": "Door3", "user": "bob", "event": "granted"},
        ]
        
        mapping = {"timestamp": "time", "device_name": "device", "user_id": "user", "event_type": "event"}
        
        validation_result = self.presenter.create_validation_status(poor_quality_data, mapping)
        # Should detect missing values and data issues
        self.assertIn("⚠️", str(validation_result))


def run_isolated_tests():
    """Run all tests in isolation"""
    print("🧪 Running Column Data Presenter Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestColumnDataPresenter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_isolated_tests()
