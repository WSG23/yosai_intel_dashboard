"""Unified Service Registry"""

import logging
from typing import Optional, Any
from .di_container import DIContainer

logger = logging.getLogger(__name__)


def get_configured_container(config_manager: Optional[Any] = None) -> DIContainer:
    """Get fully configured DI container"""
    container = DIContainer("main")
    configure_container(container, config_manager)
    return container


def configure_container(container: DIContainer, config_manager: Optional[Any] = None) -> None:
    """Configure container with all services"""
    if config_manager is None:
        from config.yaml_config import get_configuration_manager
        config_manager = get_configuration_manager()

    container.register_instance('config_manager', config_manager)
    container.register_instance('app_config', config_manager.app_config)
    container.register_instance('database_config', config_manager.database_config)
    container.register_instance('security_config', config_manager.security_config)

    container.register(
        'database_manager',
        lambda database_config: create_database_connection(database_config),
        singleton=True,
        dependencies=['database_config']
    )

    container.register(
        'analytics_service',
        lambda database_manager: create_analytics_service(database_manager),
        singleton=True,
        dependencies=['database_manager']
    )

    logger.info("✅ Container configured successfully")


def create_database_connection(config) -> Any:
    """Create database connection from config"""
    return {'type': config.type, 'status': 'connected'}


def create_analytics_service(database_manager) -> Any:
    """Create analytics service"""
    return {'database': database_manager, 'status': 'ready'}
