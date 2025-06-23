"""Service registration module"""
from core.service_container import ServiceContainer
from services.interfaces import AnalyticsServiceProtocol, FileProcessorProtocol
from services.analytics_service import AnalyticsService
from services.file_processor_service import FileProcessorService


def configure_services(container: ServiceContainer) -> None:
    """Configure all application services"""
    container.register_singleton(AnalyticsServiceProtocol, AnalyticsService)
    container.register_transient(FileProcessorProtocol, lambda: FileProcessorService())
