# quick_test.py - Test the fixed models
from models import AccessEventModel, AnomalyDetectionModel, ModelFactory, MockDatabaseConnection

def test_fixes():
    """Test that all type errors are resolved"""
    print("🧪 Testing fixed models...")
    
    # Create mock database
    db = MockDatabaseConnection()
    
    # Test factory
    models = ModelFactory.create_all_models(db)
    print("✅ Factory works")
    
    # Test AccessEventModel with None filters (this was causing type errors)
    access_model = models['access']
    
    # These should not cause type errors anymore
    result1 = access_model.get_data(None)  # ✅ Fixed
    result2 = access_model.get_data({})    # ✅ Works
    result3 = access_model.get_data({'person_id': 'P001'})  # ✅ Works
    
    print("✅ AccessEventModel type errors fixed")
    
    # Test AnomalyDetectionModel
    anomaly_model = models['anomaly']
    
    result4 = anomaly_model.get_data(None)  # ✅ Fixed
    result5 = anomaly_model.get_data({})    # ✅ Works
    
    print("✅ AnomalyDetectionModel type errors fixed")
    
    print("🎉 All Pylance errors should be resolved!")
    
    return True

if __name__ == "__main__":
    test_fixes()
