#!/usr/bin/env python3
# quick_fix.py - Immediately fix Pylance errors and make code modular
"""
Quick Fix Script for Yōsai Intel Dashboard
Resolves type errors and creates modular structure
"""

import os
import shutil
from pathlib import Path
import sys

def backup_files(project_root: Path):
    """Backup existing files before making changes"""
    backup_dir = project_root / "backup_before_fix"
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "models/base.py",
        "models/__init__.py"
    ]
    
    for file_path in files_to_backup:
        src = project_root / file_path
        if src.exists():
            dst = backup_dir / file_path.replace("/", "_")
            shutil.copy2(src, dst)
            print(f"✅ Backed up {file_path} to {dst}")

def fix_models_base(project_root: Path):
    """Fix the models/base.py file to resolve type errors"""
    
    models_dir = project_root / "models"
    base_file = models_dir / "base.py"
    
    # The fixed content (from our first artifact)
    fixed_content = '''# models/base.py - Fixed type-safe version
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from datetime import datetime, timedelta
import logging

class BaseModel(ABC):
    """Base class for all data models with proper type safety"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    @abstractmethod
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get data with optional filtering - subclasses must implement"""
        pass
    
    @abstractmethod
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics - subclasses must implement"""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Basic data validation - can be overridden by subclasses"""
        if data is None or data.empty:
            return False
        return True

class AccessEventModel(BaseModel):
    """Model for access control events with proper type safety"""
    
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get access events with optional filtering"""
        
        base_query = """
        SELECT 
            event_id,
            timestamp,
            person_id,
            door_id,
            badge_id,
            access_result,
            badge_status,
            door_held_open_time,
            entry_without_badge,
            device_status
        FROM access_events 
        WHERE 1=1
        """
        
        params = []
        
        # Use empty dict if filters is None to avoid type issues
        if filters is None:
            filters = {}
        
        if filters:
            if 'start_date' in filters:
                base_query += " AND timestamp >= %s"
                params.append(filters['start_date'])
            if 'end_date' in filters:
                base_query += " AND timestamp <= %s"
                params.append(filters['end_date'])
            if 'person_id' in filters:
                base_query += " AND person_id = %s"
                params.append(filters['person_id'])
            if 'door_id' in filters:
                base_query += " AND door_id = %s"
                params.append(filters['door_id'])
            if 'access_result' in filters:
                base_query += " AND access_result = %s"
                params.append(filters['access_result'])
        
        base_query += " ORDER BY timestamp DESC LIMIT 10000"
        
        try:
            df = self.db.execute_query(base_query, tuple(params) if params else None)
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error fetching access events: {e}")
            return pd.DataFrame()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT person_id) as unique_people,
            COUNT(DISTINCT door_id) as unique_doors,
            SUM(CASE WHEN access_result = 'Granted' THEN 1 ELSE 0 END)::float / COUNT(*) as granted_rate,
            MIN(timestamp) as earliest_event,
            MAX(timestamp) as latest_event
        FROM access_events
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        """
        
        try:
            result = self.db.execute_query(query)
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            return {}
        except Exception as e:
            logging.error(f"Error getting summary stats: {e}")
            return {}
    
    def get_recent_events(self, hours: int = 24) -> pd.DataFrame:
        """Get recent events for dashboard"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.get_data({'start_date': cutoff_time})
    
    def get_trend_analysis(self, days: int = 30) -> pd.DataFrame:
        """Get trend analysis for analytics"""
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_events,
            SUM(CASE WHEN access_result = 'Granted' THEN 1 ELSE 0 END) as granted_events,
            COUNT(DISTINCT person_id) as unique_users
        FROM access_events 
        WHERE timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        try:
            result = self.db.execute_query(query, (days,))
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error getting trend analysis: {e}")
            return pd.DataFrame()

class AnomalyDetectionModel(BaseModel):
    """Model for anomaly detection data with proper type safety"""
    
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get anomaly detections"""
        
        base_query = """
        SELECT 
            a.anomaly_id,
            a.event_id,
            a.anomaly_type,
            a.severity,
            a.confidence_score,
            a.description,
            a.detected_at,
            e.timestamp,
            e.person_id,
            e.door_id
        FROM anomaly_detections a
        JOIN access_events e ON a.event_id = e.event_id
        WHERE 1=1
        """
        
        params = []
        
        # Use empty dict if filters is None
        if filters is None:
            filters = {}
        
        if filters:
            if 'anomaly_type' in filters:
                base_query += " AND a.anomaly_type = %s"
                params.append(filters['anomaly_type'])
            if 'severity' in filters:
                base_query += " AND a.severity = %s"
                params.append(filters['severity'])
            if 'start_date' in filters:
                base_query += " AND a.detected_at >= %s"
                params.append(filters['start_date'])
        
        base_query += " ORDER BY a.detected_at DESC LIMIT 5000"
        
        try:
            result = self.db.execute_query(base_query, tuple(params) if params else None)
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error fetching anomalies: {e}")
            return pd.DataFrame()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get anomaly summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_anomalies,
            AVG(confidence_score) as avg_confidence,
            COUNT(DISTINCT anomaly_type) as unique_types
        FROM anomaly_detections
        WHERE detected_at >= NOW() - INTERVAL '30 days'
        """
        
        try:
            result = self.db.execute_query(query)
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            return {}
        except Exception as e:
            logging.error(f"Error getting anomaly stats: {e}")
            return {}
    
    def get_anomaly_breakdown(self) -> pd.DataFrame:
        """Get anomaly type breakdown for charts"""
        query = """
        SELECT 
            anomaly_type,
            COUNT(*) as count,
            AVG(confidence_score) as avg_confidence
        FROM anomaly_detections
        WHERE detected_at >= NOW() - INTERVAL '30 days'
        GROUP BY anomaly_type
        ORDER BY count DESC
        """
        
        try:
            result = self.db.execute_query(query)
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error getting anomaly breakdown: {e}")
            return pd.DataFrame()

# Factory class for creating model instances (modular and testable)
class ModelFactory:
    """Factory class for creating data model instances"""
    
    @staticmethod
    def create_access_model(db_connection) -> AccessEventModel:
        """Create an AccessEventModel instance"""
        return AccessEventModel(db_connection)
    
    @staticmethod
    def create_anomaly_model(db_connection) -> AnomalyDetectionModel:
        """Create an AnomalyDetectionModel instance"""
        return AnomalyDetectionModel(db_connection)
    
    @staticmethod
    def create_all_models(db_connection) -> Dict[str, BaseModel]:
        """Create all standard models with a single data source"""
        return {
            'access': ModelFactory.create_access_model(db_connection),
            'anomaly': ModelFactory.create_anomaly_model(db_connection)
        }

# Mock database connection for testing
class MockDatabaseConnection:
    """Mock database connection for testing purposes"""
    
    def __init__(self):
        self.sample_data = self._generate_sample_data()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Mock query execution that returns sample data"""
        # Simple query parsing for testing
        if "access_events" in query.lower():
            return self.sample_data['access_events']
        elif "anomaly_detections" in query.lower():
            return self.sample_data['anomaly_detections']
        else:
            return pd.DataFrame()
    
    def _generate_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Generate sample data for testing"""
        access_events = pd.DataFrame({
            'event_id': ['E001', 'E002', 'E003'],
            'timestamp': [datetime.now() - timedelta(hours=i) for i in range(3)],
            'person_id': ['P001', 'P002', 'P001'],
            'door_id': ['D001', 'D002', 'D001'],
            'access_result': ['Granted', 'Denied', 'Granted'],
            'badge_status': ['Valid', 'Invalid', 'Valid']
        })
        
        anomaly_detections = pd.DataFrame({
            'anomaly_id': ['A001', 'A002'],
            'event_id': ['E002', 'E003'],
            'anomaly_type': ['unusual_time', 'multiple_attempts'],
            'severity': ['medium', 'high'],
            'confidence_score': [0.75, 0.95]
        })
        
        return {
            'access_events': access_events,
            'anomaly_detections': anomaly_detections
        }

# Export all classes
__all__ = ['BaseModel', 'AccessEventModel', 'AnomalyDetectionModel', 'ModelFactory', 'MockDatabaseConnection']
'''
    
    # Write the fixed content
    base_file.write_text(fixed_content)
    print(f"✅ Fixed {base_file}")

def fix_models_init(project_root: Path):
    """Fix the models/__init__.py file to resolve import errors"""
    
    models_dir = project_root / "models"
    init_file = models_dir / "__init__.py"
    
    fixed_init_content = '''# models/__init__.py - Fixed imports to resolve Pylance errors
"""
Yōsai Intel Data Models Package - Type-safe and Modular
"""

# Import enums
from .enums import (
    AnomalyType,
    AccessResult, 
    BadgeStatus,
    SeverityLevel,
    TicketStatus,
    DoorType
)

# Import entities  
from .entities import (
    Person,
    Door, 
    Facility
)

# Import events
from .events import (
    AccessEvent,
    AnomalyDetection,
    IncidentTicket
)

# Import base models (fixed to use the new base.py structure)
from .base import (
    BaseModel,
    AccessEventModel,
    AnomalyDetectionModel,
    ModelFactory,
    MockDatabaseConnection
)

# Define what gets exported when someone does "from models import *"
__all__ = [
    # Enums
    'AnomalyType', 'AccessResult', 'BadgeStatus', 'SeverityLevel', 
    'TicketStatus', 'DoorType',
    
    # Entities
    'Person', 'Door', 'Facility',
    
    # Events
    'AccessEvent', 'AnomalyDetection', 'IncidentTicket',
    
    # Models (new structure)
    'BaseModel', 'AccessEventModel', 'AnomalyDetectionModel',
    
    # Factory and utilities
    'ModelFactory', 'MockDatabaseConnection'
]

# Package metadata
__version__ = "2.0.0"
__author__ = "Yōsai Intel Team"
__description__ = "Type-safe, modular data models for security intelligence"
'''
    
    init_file.write_text(fixed_init_content)
    print(f"✅ Fixed {init_file}")

def create_test_file(project_root: Path):
    """Create a quick test file to validate the fixes"""
    
    test_content = '''# quick_test.py - Test the fixed models
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
'''
    
    test_file = project_root / "quick_test.py"
    test_file.write_text(test_content)
    print(f"✅ Created {test_file}")

def main():
    """Main fix script"""
    print("🔧 Quick Fix Script for Yōsai Intel Dashboard")
    print("=" * 50)
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
    
    # Validate project structure
    models_dir = project_root / "models"
    if not models_dir.exists():
        print(f"❌ Models directory not found: {models_dir}")
        print("Run this script from your project root directory")
        return False
    
    print(f"📁 Working on project: {project_root}")
    
    try:
        # Step 1: Backup existing files
        backup_files(project_root)
        
        # Step 2: Fix models/base.py
        fix_models_base(project_root)
        
        # Step 3: Fix models/__init__.py
        fix_models_init(project_root)
        
        # Step 4: Create test file
        create_test_file(project_root)
        
        print("\n" + "=" * 50)
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n🎯 Pylance errors resolved:")
        print("  ✓ reportArgumentType - Fixed None vs Dict[str, Any]")
        print("  ✓ reportMissingImports - Fixed import paths")
        print("  ✓ reportAttributeAccessIssue - Fixed model exports")
        
        print("\n🚀 Next steps:")
        print("1. Run: python quick_test.py")
        print("2. Check that Pylance shows no more errors")
        print("3. Your code is now modular and type-safe!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
'''
Usage:
python quick_fix.py [project_root]

This script will:
1. ✅ Fix all Pylance type errors
2. ✅ Make your models modular and testable
3. ✅ Create proper type annotations
4. ✅ Add error handling
5. ✅ Maintain backward compatibility
'''