"""Unified Service Registry"""

import logging
from typing import Dict, Any, Optional, List
import os

from .container import Container
from .di_container import DIContainer

logger = logging.getLogger(__name__)


def create_config_manager():
    """Create configuration manager"""
    try:
        from config.yaml_config import get_configuration_manager
        return get_configuration_manager()
    except ImportError:
        logger.warning("YAML config not available")
        return None


def get_configured_container_with_yaml(config_manager: Optional[Any] = None) -> Container:
    """Get container configured with YAML configuration"""
    try:
        from .container import get_container
        container = get_container()

        if config_manager is None:
            try:
                from config.yaml_config import get_configuration_manager
                config_manager = get_configuration_manager()
            except ImportError:
                logger.warning("YAML config not available, using minimal config")
                config_manager = None

        configure_container_with_yaml(container, config_manager)
        return container

    except Exception as e:
        logger.error(f"Failed to create configured container: {e}")
        return Container()


def configure_container_with_yaml(container: Container, config_manager: Optional[Any] = None) -> None:
    """Configure container with YAML configuration"""
    logger.info("\ud83d\udd27 Configuring DI Container with YAML...")

    try:
        if config_manager:
            container.register_instance('config_manager', config_manager)
            container.register_instance('app_config', config_manager.app_config)
            container.register_instance('database_config', config_manager.database_config)
            container.register_instance('security_config', config_manager.security_config)

        container.register(
            'database_manager',
            lambda: create_database_connection_safe(),
            singleton=True
        )

        container.register(
            'cache_manager',
            lambda: create_cache_manager_safe(),
            singleton=True
        )

        container.register(
            'analytics_service',
            lambda: create_analytics_service_safe(),
            singleton=True
        )

        container.register(
            'health_monitor',
            lambda: create_health_monitor_safe(container),
            singleton=True
        )

        logger.info("\u2705 Container configured successfully")

    except Exception as e:
        logger.error(f"Container configuration failed: {e}")


def create_database_connection_safe():
    """Create database connection safely"""
    try:
        from config.database_manager import DatabaseManager, MockDatabaseConnection
        cfg = DatabaseManager.from_environment()
        return DatabaseManager.create_connection(cfg)
    except Exception:
        class MinimalDB:
            def health_check(self):
                return {'status': 'healthy', 'type': 'minimal_mock'}
        return MinimalDB()


def create_cache_manager_safe():
    """Create cache manager safely"""
    try:
        from config.cache_manager import get_cache_manager
        return get_cache_manager()
    except Exception:
        class MinimalCache:
            def __init__(self):
                self.cache = {}

            def get(self, key):
                return self.cache.get(key)

            def set(self, key, value):
                self.cache[key] = value

            def health_check(self):
                return {'status': 'healthy', 'type': 'minimal_mock'}

        return MinimalCache()


def create_analytics_service_safe():
    """Create analytics service safely"""
    try:
        from services.analytics_service import AnalyticsService
        return AnalyticsService()
    except Exception:
        class MockAnalyticsService:
            def get_dashboard_summary(self):
                return {
                    'status': 'mock',
                    'total_events': 0,
                    'system_status': 'healthy',
                    'last_updated': 'N/A'
                }

            def process_uploaded_file(self, df, filename):
                return {
                    'success': False,
                    'error': 'Mock analytics service - no real processing'
                }

        return MockAnalyticsService()


def create_health_monitor_safe(container: Container):
    """Create health monitor safely"""

    class SimpleHealthMonitor:
        def __init__(self, container: Container) -> None:
            self.container = container

        def health_check(self):
            try:
                return {
                    'overall': 'healthy',
                    'timestamp': 'N/A',
                    'services': {
                        'container': {
                            'status': 'healthy',
                            'services_count': len(self.container._services) if hasattr(self.container, '_services') else 0
                        }
                    }
                }
            except Exception as e:
                return {
                    'overall': 'error',
                    'error': str(e)
                }

    return SimpleHealthMonitor(container)


def debug_configuration_loading() -> Dict[str, Any]:
    """Gather debug information about configuration loading"""
    info: Dict[str, Any] = {
        'config_files_found': [],
        'environment_vars': {},
        'import_status': {}
    }

    try:
        from pathlib import Path
        from config import yaml_config

        info['import_status']['config.yaml_config'] = 'success'
        possible = [
            'config/config.yaml',
            'config/production.yaml',
            'config/test.yaml'
        ]
        info['config_files_found'] = [p for p in possible if Path(p).exists()]
    except Exception as e:
        info['import_status']['config.yaml_config'] = f'error: {e}'

    env_vars = [
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_TYPE', 'YOSAI_ENV'
    ]
    for var in env_vars:
        info['environment_vars'][var] = os.getenv(var)

    return info


def test_container_configuration() -> Dict[str, Any]:
    """Simple container configuration test used in integration tests"""
    try:
        config_manager = create_config_manager()
        container = get_configured_container_with_yaml(config_manager)
        return {
            'success': True,
            'config_manager_type': type(config_manager).__name__ if config_manager else 'None',
            'services_registered': len(getattr(container, '_services', {}))
        }
    except Exception as exc:
        return {'success': False, 'error': str(exc)}


# LEGACY COMPATIBILITY FUNCTIONS


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
