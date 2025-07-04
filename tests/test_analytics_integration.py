#!/usr/bin/env python3
"""
Complete Integration Tests for Analytics System
"""
import pytest
pytest.importorskip("pandas")
import pandas as pd
from services.analytics_service import get_analytics_service
from services.file_ingestion import FileIngestionAnalytics
from services.database_analytics import DatabaseAnalytics
from services.uploaded_data_analytics import UploadedDataAnalytics
from models.base import ModelFactory


def test_analytics_service_creation():
    """Test analytics service can be created"""
    service = get_analytics_service()
    assert service is not None
    assert hasattr(service, 'health_check')


def test_analytics_with_sample_data():
    """Test analytics generation with sample data"""
    service = get_analytics_service()
    result = service.get_analytics_by_source("sample")

    assert result['status'] == 'success'
    assert 'total_rows' in result
    assert result['total_rows'] > 0


def test_model_factory():
    """Test model factory creates models correctly"""
    df = pd.DataFrame({
        'user_id': ['user1', 'user2'],
        'door_id': ['door1', 'door2'],
        'access_result': ['Granted', 'Denied']
    })

    models = ModelFactory.create_models_from_dataframe(df)
    assert 'access' in models
    assert 'anomaly' in models


def test_health_check():
    """Test service health check"""
    service = get_analytics_service()
    health = service.health_check()

    assert 'service' in health
    assert health['service'] == 'healthy'
    assert 'timestamp' in health


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
