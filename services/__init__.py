"""
Services package for Yōsai Intel Dashboard
"""
from .base import BaseService, MockService
from .protocols import DatabaseProtocol, AnalyticsProtocol, FileProcessorProtocol
from .analytics_service import AnalyticsService, create_analytics_service

# Only import if file exists
try:
    from .file_processor_service import FileProcessorService
except ImportError:
    FileProcessorService = None

try:
    from .service_registry import register_all_services, get_service
except ImportError:
    register_all_services = None
    get_service = None

__all__ = [
    'BaseService',
    'MockService', 
    'DatabaseProtocol',
    'AnalyticsProtocol',
    'FileProcessorProtocol',
    'AnalyticsService',
    'create_analytics_service',
    'FileProcessorService',
    'register_all_services',
    'get_service'
]
