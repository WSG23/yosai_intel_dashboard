# test_modular_system.py - FIXED: Complete modular system validation
"""
Comprehensive test suite for Yōsai Intel Dashboard modular architecture
Tests all components, services, models, and integrations
"""

import os
import sys
import unittest
import logging
import importlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Configure test logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests

class ModularityValidator:
    """Validates the modular architecture of the application"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: Dict[str, Dict[str, Any]] = {}
        self.import_errors: List[str] = []
        
    def validate_project_structure(self) -> Dict[str, bool]:
        """Validate that all required directories and files exist"""
        
        required_structure = {
            'config/': ['__init__.py', 'database_manager.py'],
            'models/': ['__init__.py', 'base.py', 'entities.py', 'events.py', 'enums.py', 'access_events.py'],
            'services/': ['__init__.py', 'analytics_service.py'],
            'components/': ['__init__.py', 'navbar.py'],
            'components/analytics/': ['__init__.py', 'file_uploader.py', 'data_preview.py', 'analytics_charts.py'],
            'pages/': ['__init__.py', 'deep_analytics.py', 'file_upload.py'],
            'utils/': ['__init__.py'],
            'assets/css/': ['main.css'],
            '.': ['app.py', 'requirements.txt']
        }
        
        validation_results = {}
        
        for directory, files in required_structure.items():
            dir_path = self.project_root / directory
            validation_results[f"dir_{directory}"] = dir_path.exists()
            
            for file in files:
                file_path = dir_path / file
                validation_results[f"file_{directory}{file}"] = file_path.exists()
        
        return validation_results
    
    def test_imports(self) -> Dict[str, bool]:
        """Test that all modules can be imported successfully"""
        
        modules_to_test = [
            'config.database_manager',
            'models.base',
            'models.entities',
            'models.events',
            'models.enums',
            'models.access_events',
            'services.analytics_service',
            'components.navbar',
            'components.analytics',
            'pages.deep_analytics',
            'pages.file_upload'
        ]
        
        import_results = {}
        
        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                import_results[module_name] = True
            except ImportError as e:
                import_results[module_name] = False
                self.import_errors.append(f"{module_name}: {e}")
        
        return import_results
    
    def test_component_isolation(self) -> Dict[str, bool]:
        """Test that components can be imported and used independently"""
        
        isolation_results = {}
        
        # Test database manager isolation
        try:
            from config.database_manager import DatabaseManager, DatabaseConfig, MockDatabaseConnection
            
            # Test mock connection creation
            mock_conn = MockDatabaseConnection()
            test_df = mock_conn.execute_query("SELECT * FROM access_events LIMIT 5")
            isolation_results['database_manager'] = not test_df.empty
            
        except Exception as e:
            isolation_results['database_manager'] = False
            self.import_errors.append(f"Database manager isolation: {e}")
        
        # Test analytics service isolation
        try:
            from services.analytics_service import create_analytics_service, AnalyticsConfig
            
            service = create_analytics_service(AnalyticsConfig())
            summary = service.get_dashboard_summary()
            isolation_results['analytics_service'] = isinstance(summary, dict)
            
        except Exception as e:
            isolation_results['analytics_service'] = False
            self.import_errors.append(f"Analytics service isolation: {e}")
        
        # Test analytics components isolation
        try:
            from components.analytics import (
                create_file_uploader,
                create_data_preview,
                create_analytics_charts,
                FileProcessor
            )
            
            # Test component creation
            uploader = create_file_uploader()
            sample_df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
            preview = create_data_preview(sample_df, "test.csv")
            
            isolation_results['analytics_components'] = uploader is not None and preview is not None
            
        except Exception as e:
            isolation_results['analytics_components'] = False
            self.import_errors.append(f"Analytics components isolation: {e}")
        
        return isolation_results
    
    def test_type_safety(self) -> Dict[str, bool]:
        """Test type safety across the modular system"""
        
        type_safety_results = {}
        
        # Test models type safety
        try:
            from models.entities import Person, Door, Facility
            from models.events import AccessEvent, AnomalyDetection
            from models.enums import AccessResult, SeverityLevel
            
            # Create instances with proper types
            person = Person(person_id="TEST001", name="Test User")
            door = Door(door_id="DOOR001", door_name="Test Door", facility_id="FAC001", area_id="AREA001")
            event = AccessEvent(
                event_id="EVT001",
                timestamp=datetime.now(),
                person_id="TEST001",
                door_id="DOOR001",
                access_result=AccessResult.GRANTED
            )
            
            # Test serialization
            person_dict = person.to_dict()
            event_dict = event.to_dict()
            
            type_safety_results['models_creation'] = (
                isinstance(person_dict, dict) and 
                isinstance(event_dict, dict) and
                person_dict['person_id'] == "TEST001"
            )
            
        except Exception as e:
            type_safety_results['models_creation'] = False
            self.import_errors.append(f"Models type safety: {e}")
        
        # Test services type safety
        try:
            from services.analytics_service import AnalyticsService, AnalyticsConfig
            from config.database_manager import MockDatabaseConnection
            
            config = AnalyticsConfig(default_time_range_days=7)
            service = AnalyticsService(config)
            
            # Test with typed inputs
            sample_data = pd.DataFrame({
                'person_id': ['EMP001', 'EMP002'],
                'door_id': ['DOOR001', 'DOOR002'],
                'access_result': ['Granted', 'Denied'],
                'timestamp': [datetime.now(), datetime.now() - timedelta(hours=1)]
            })
            
            result = service.process_uploaded_file(sample_data, "test.csv")
            
            type_safety_results['services_type_safety'] = (
                isinstance(result, dict) and
                'success' in result and
                isinstance(result['success'], bool)
            )
            
        except Exception as e:
            type_safety_results['services_type_safety'] = False
            self.import_errors.append(f"Services type safety: {e}")
        
        return type_safety_results
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of the modular system"""
        
        print("🔍 Running Comprehensive Modular System Validation...")
        print("=" * 60)
        
        validation_results = {
            'project_structure': self.validate_project_structure(),
            'import_tests': self.test_imports(),
            'component_isolation': self.test_component_isolation(),
            'type_safety': self.test_type_safety(),
            'import_errors': self.import_errors
        }
        
        # Calculate overall scores
        structure_score = sum(validation_results['project_structure'].values()) / len(validation_results['project_structure'])
        import_score = sum(validation_results['import_tests'].values()) / len(validation_results['import_tests'])
        isolation_score = sum(validation_results['component_isolation'].values()) / len(validation_results['component_isolation'])
        type_score = sum(validation_results['type_safety'].values()) / len(validation_results['type_safety'])
        
        validation_results['scores'] = {
            'structure': structure_score * 100,
            'imports': import_score * 100,
            'isolation': isolation_score * 100,
            'type_safety': type_score * 100,
            'overall': (structure_score + import_score + isolation_score + type_score) / 4 * 100
        }
        
        return validation_results

class IntegrationTester(unittest.TestCase):
    """Integration tests for the modular system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = pd.DataFrame({
            'event_id': ['EVT001', 'EVT002', 'EVT003'],
            'timestamp': [datetime.now() - timedelta(hours=i) for i in range(3)],
            'person_id': ['EMP001', 'EMP002', 'EMP001'],
            'door_id': ['DOOR001', 'DOOR002', 'DOOR001'],
            'access_result': ['Granted', 'Denied', 'Granted']
        })
    
    def test_database_service_integration(self):
        """Test database and service integration"""
        try:
            from config.database_manager import DatabaseManager, DatabaseConfig
            from services.analytics_service import create_analytics_service
            
            # Create mock database
            config = DatabaseConfig(db_type='mock')
            db_conn = DatabaseManager.create_connection(config)
            
            # Test database operations
            result = db_conn.execute_query("SELECT * FROM access_events LIMIT 5")
            self.assertIsInstance(result, pd.DataFrame)
            
            # Test service with database
            analytics_service = create_analytics_service()
            summary = analytics_service.get_dashboard_summary()
            self.assertIsInstance(summary, dict)
            
        except Exception as e:
            self.fail(f"Database-service integration failed: {e}")
    
    def test_analytics_pipeline_integration(self):
        """Test complete analytics pipeline"""
        try:
            from components.analytics import FileProcessor, AnalyticsGenerator
            from services.analytics_service import create_analytics_service
            
            # Test file processing
            valid, message, suggestions = FileProcessor.validate_dataframe(self.test_data)
            self.assertTrue(valid, f"Data validation failed: {message}")
            
            # Test analytics generation
            analytics = AnalyticsGenerator.generate_analytics(self.test_data)
            self.assertIsInstance(analytics, dict)
            self.assertIn('total_events', analytics)
            
            # Test service integration
            service = create_analytics_service()
            result = service.process_uploaded_file(self.test_data, "test.csv")
            self.assertTrue(result.get('success', False))
            
        except Exception as e:
            self.fail(f"Analytics pipeline integration failed: {e}")
    
    def test_component_rendering(self):
        """Test that components can be rendered"""
        try:
            from components.analytics import (
                create_file_uploader,
                create_data_preview,
                create_analytics_charts
            )
            
            # Test component creation
            uploader = create_file_uploader()
            self.assertIsNotNone(uploader)
            
            preview = create_data_preview(self.test_data, "test.csv")
            self.assertIsNotNone(preview)
            
            # Test with analytics data
            analytics_data = {
                'access_patterns': {'Granted': 2, 'Denied': 1},
                'total_events': 3
            }
            charts = create_analytics_charts(analytics_data)
            self.assertIsNotNone(charts)
            
        except Exception as e:
            self.fail(f"Component rendering failed: {e}")

def print_validation_report(results: Dict[str, Any]) -> None:
    """Print formatted validation report"""
    
    print("\n📊 MODULAR SYSTEM VALIDATION REPORT")
    print("=" * 60)
    
    scores = results.get('scores', {})
    overall_score = scores.get('overall', 0)
    
    # Overall status
    if overall_score >= 90:
        status = "🟢 EXCELLENT"
        message = "Modular architecture is excellent!"
    elif overall_score >= 80:
        status = "🟡 GOOD"
        message = "Good modular architecture with minor issues"
    elif overall_score >= 70:
        status = "🟠 NEEDS IMPROVEMENT"
        message = "Modular architecture needs some work"
    else:
        status = "🔴 CRITICAL"
        message = "Major modular architecture issues found"
    
    print(f"\n{status} - Overall Score: {overall_score:.1f}/100")
    print(f"{message}")
    
    # Individual scores
    print(f"\n📏 DETAILED SCORES:")
    print(f"  🏗️  Project Structure: {scores.get('structure', 0):.1f}%")
    print(f"  📦 Import Success: {scores.get('imports', 0):.1f}%")
    print(f"  🔗 Component Isolation: {scores.get('isolation', 0):.1f}%")
    print(f"  🛡️  Type Safety: {scores.get('type_safety', 0):.1f}%")
    
    # Failed imports
    import_errors = results.get('import_errors', [])
    if import_errors:
        print(f"\n❌ IMPORT ERRORS ({len(import_errors)}):")
        for error in import_errors[:5]:  # Show first 5 errors
            print(f"  • {error}")
        if len(import_errors) > 5:
            print(f"  ... and {len(import_errors) - 5} more errors")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if scores.get('structure', 0) < 90:
        print("  • Complete missing files and directories")
    if scores.get('imports', 0) < 90:
        print("  • Fix import errors and dependencies")
    if scores.get('isolation', 0) < 90:
        print("  • Improve component isolation and independence")
    if scores.get('type_safety', 0) < 90:
        print("  • Add proper type annotations and validation")
    
    if overall_score >= 90:
        print("  ✅ Great job! Your modular architecture is excellent.")

def run_integration_tests() -> bool:
    """Run integration tests"""
    print("\n🧪 Running Integration Tests...")
    print("-" * 40)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(IntegrationTester))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

def main():
    """Main execution function"""
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path(".")
    
    if not project_root.exists():
        print(f"❌ Project directory not found: {project_root}")
        sys.exit(1)
    
    print("🚀 YŌSAI INTEL MODULAR SYSTEM VALIDATION")
    print("=" * 60)
    print(f"Project Root: {project_root.absolute()}")
    
    # Run modular validation
    validator = ModularityValidator(project_root)
    validation_results = validator.run_full_validation()
    print_validation_report(validation_results)
    
    # Run integration tests
    integration_success = run_integration_tests()
    
    # Final summary
    overall_score = validation_results.get('scores', {}).get('overall', 0)
    
    print("\n" + "=" * 60)
    print("🎯 FINAL SUMMARY")
    print("=" * 60)
    
    if overall_score >= 90 and integration_success:
        print("🎉 SUCCESS! Your modular architecture is excellent!")
        print("✅ All components are properly isolated and testable")
        print("✅ Type safety is maintained throughout")
        print("✅ Integration tests pass")
        print("\n🚀 Ready for production deployment!")
        return True
    else:
        print("⚠️  Issues found in modular architecture")
        print(f"Validation Score: {overall_score:.1f}/100")
        print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
        print("\n🔧 Please address the issues above before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)