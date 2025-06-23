"""
Service isolation testing framework
"""
import pytest
import pandas as pd
from typing import Any, Dict
from unittest.mock import Mock

class TestDatabaseService:
    """Test database service isolation"""
    
    def test_mock_database_connection(self):
        """Test mock database can be created independently"""
        from config.database_manager import MockDatabaseConnection
        
        db = MockDatabaseConnection()
        result = db.execute_query("SELECT * FROM test")
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'event_id' in result.columns
    
    def test_database_manager_factory(self):
        """Test database manager factory pattern"""
        from config.database_manager import DatabaseManager, DatabaseConfig
        
        config = DatabaseConfig(type="mock")
        db = DatabaseManager.create_connection(config)
        
        result = db.execute_query("SELECT 1")
        assert isinstance(result, pd.DataFrame)

class TestAnalyticsService:
    """Test analytics service isolation"""
    
    def setup_method(self):
        """Setup test data"""
        self.sample_data = pd.DataFrame({
            'event_id': ['EVT001', 'EVT002', 'EVT003'],
            'person_id': ['EMP001', 'EMP002', 'EMP001'],
            'door_id': ['DOOR001', 'DOOR002', 'DOOR001'],
            'access_result': ['Granted', 'Denied', 'Granted'],
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='H')
        })
    
    def test_analytics_service_creation(self):
        """Test analytics service can be created independently"""
        from services.analytics_service import AnalyticsService
        
        service = AnalyticsService()
        assert service is not None
    
    def test_access_pattern_analysis(self):
        """Test access pattern analysis in isolation"""
        from services.analytics_service import AnalyticsService
        
        service = AnalyticsService()
        result = service.analyze_access_patterns(self.sample_data)
        
        assert 'total_events' in result
        assert result['total_events'] == 3
        assert 'access_patterns' in result
        assert 'unique_users' in result
    
    def test_anomaly_detection(self):
        """Test anomaly detection in isolation"""
        from services.analytics_service import AnalyticsService
        
        service = AnalyticsService()
        events = self.sample_data.to_dict('records')
        anomalies = service.detect_anomalies(events)
        
        assert isinstance(anomalies, list)

class TestServiceContainer:
    """Test service container isolation"""
    
    def test_container_creation(self):
        """Test container can be created independently"""
        from core.service_container import ServiceContainer
        
        container = ServiceContainer()
        assert container is not None
    
    def test_service_registration(self):
        """Test service registration and retrieval"""
        from core.service_container import ServiceContainer
        
        container = ServiceContainer()
        
        # Register mock service
        mock_service = Mock()
        container.register_instance('test_service', mock_service)
        
        # Retrieve service
        retrieved = container.get('test_service')
        assert retrieved is mock_service
    
    def test_singleton_behavior(self):
        """Test singleton services return same instance"""
        from core.service_container import ServiceContainer
        
        container = ServiceContainer()
        
        # Register singleton factory
        call_count = 0
        def factory():
            nonlocal call_count
            call_count += 1
            return Mock()
        
        container.register_singleton('singleton_service', factory)
        
        # Get service twice
        service1 = container.get('singleton_service')
        service2 = container.get('singleton_service')
        
        # Should be same instance
        assert service1 is service2
        assert call_count == 1

# Run with: python -m pytest tests/test_service_isolation.py -v

