"""Pytest configuration and shared fixtures"""
import pytest
from core.container import TestContainer
from config.config_manager import Config, DatabaseConfig, AppConfig
from database.connection import MockConnection
from services.analytics import AnalyticsService

@pytest.fixture
def test_config():
    return Config(
        database=DatabaseConfig(type="mock", name=":memory:"),
        app=AppConfig(debug=True, environment="test")
    )

@pytest.fixture
def test_container(test_config):
    with TestContainer() as container:
        container.register_instance('config', test_config)
        container.register_instance('database_connection', MockConnection())
        container.register_singleton(
            'analytics_service',
            lambda: AnalyticsService(container.get('database_connection'))
        )
        yield container

@pytest.fixture
def mock_db():
    return MockConnection()

@pytest.fixture
def analytics_service(mock_db):
    return AnalyticsService(mock_db)
