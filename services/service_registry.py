"""Service registration module"""
from __future__ import annotations

from typing import Any, Optional

from core.service_container import ServiceContainer
from services.protocols import (
    AnalyticsProtocol,
    DatabaseProtocol,
    FileProcessorProtocol,
)
from services.analytics_service import AnalyticsService
from services.file_processor_service import FileProcessorService
from config.database_manager import DatabaseManager


_container: Optional[ServiceContainer] = None


def configure_services(container: ServiceContainer) -> None:
    """Configure all application services"""
    container.register_singleton(
        'database', DatabaseManager.from_environment
    )
    container.register_singleton(
        'analytics_service',
        lambda: AnalyticsService(container.get('database')),
    )
    container.register_factory('file_processor', FileProcessorService)


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


def get_analytics_service() -> AnalyticsProtocol:
    """Typed accessor for the analytics service"""
    return get_service('analytics_service')  # type: ignore[return-value]


def get_database() -> DatabaseProtocol:
    """Typed accessor for the database service"""
    return get_service('database')  # type: ignore[return-value]


def get_file_processor() -> FileProcessorProtocol:
    """Typed accessor for the file processor service"""
    return get_service('file_processor')  # type: ignore[return-value]


__all__ = [
    'ServiceContainer',
    'configure_services',
    'register_all_services',
    'get_service',
    'get_analytics_service',
    'get_database',
    'get_file_processor',
]
