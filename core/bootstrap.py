"""
Application bootstrap with simplified service registration
"""
from config.simple_config import get_config
from core.simple_container import get_container
from services.analytics_service import AnalyticsService
import logging

logger = logging.getLogger(__name__)


def bootstrap_application() -> None:
    """Bootstrap application with all services"""
    config = get_config()
    container = get_container()
    container.register_instance('config', config)
    container.register_singleton('analytics_service', lambda: AnalyticsService())
    from config.database_manager import MockDatabaseConnection
    container.register_singleton('database', lambda: MockDatabaseConnection())
    logger.info("✅ Application bootstrapped successfully")


def get_service(name: str) -> Any:
    """Convenience function to get services"""
    container = get_container()
    return container.get(name)
