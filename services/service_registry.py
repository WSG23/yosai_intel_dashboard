"""Service registration module"""

from core.dependency_container import ServiceContainer
from services.protocols import AnalyticsProtocol, FileProcessorProtocol

from services.analytics_service import AnalyticsService
from services.file_processor_service import FileProcessorService


def configure_services(container: ServiceContainer) -> None:
    """Configure all application services"""
    container.register_singleton(AnalyticsProtocol, AnalyticsService)
    container.register_transient(FileProcessorProtocol, lambda: FileProcessorService())
