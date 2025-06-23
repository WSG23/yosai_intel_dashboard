"""Service registration module"""
from __future__ import annotations

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# Import core service container
from core.service_container import ServiceContainer

# Import protocols and services
from .protocols import (
    AnalyticsProtocol,
    DatabaseProtocol,
    FileProcessorProtocol,
)

from .analytics_service import AnalyticsService
from .file_processor_service import FileProcessorService

# Import database manager
try:
    from config.database_manager import DatabaseManager
except ImportError:
    logger.warning("DatabaseManager not available, using mock")
    DatabaseManager = None

_container: Optional[ServiceContainer] = None

def configure_services(container: ServiceContainer) -> None:
    """Configure all application services"""
    try:
        # Register database
        if DatabaseManager:
            container.register_singleton('database', DatabaseManager.from_environment)
        else:
            # Mock database for development
            container.register_singleton('database', lambda: MockDatabase())
        
        # Register analytics service
        container.register_singleton(
            'analytics_service',
            lambda: AnalyticsService(container.get('database')),
        )
        
        # Register file processor
        container.register_factory('file_processor', FileProcessorService)
        
        logger.info("✅ Services configured successfully")
        
    except Exception as e:
        logger.error(f"Failed to configure services: {e}")
        raise

def register_all_services(container: Optional[ServiceContainer] = None) -> ServiceContainer:
    """Create and configure a container with all default services"""
    global _container
    if container is None:
        container = ServiceContainer()
    configure_services(container)
    _container = container
    return container

def get_service(name: str) -> Any:
    """Get a service from the global container"""
    if _container is None:
        register_all_services()
    assert _container is not None
    return _container.get(name)

# Mock database for development
class MockDatabase:
    def execute_query(self, query, params=None):
        import pandas as pd
        return pd.DataFrame()
    
    def execute_command(self, command, params=None):
        return True
    
    def health_check(self):
        return {'status': 'healthy', 'type': 'mock'}

__all__ = [
    'ServiceContainer',
    'configure_services', 
    'register_all_services',
    'get_service',
]
