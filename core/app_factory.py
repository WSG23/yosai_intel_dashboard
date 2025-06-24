import dash
import logging
from typing import Optional
from core.unified_container import get_container
from config.unified_config import get_config

logger = logging.getLogger(__name__)

class AppFactory:
    """Creates and configures the main application"""

    @staticmethod
    def create_app() -> dash.Dash:
        """Create fully configured Dash application"""
        try:
            # Load configuration
            config = get_config()

            # Get service container
            container = get_container()

            # Register core services
            AppFactory._register_services(container, config)

            # Create Dash app
            app = AppFactory._create_dash_app(config)

            # Register layouts and callbacks
            AppFactory._register_layouts(app, container)

            logger.info("✅ Application created successfully")
            return app

        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise

    @staticmethod
    def _register_services(container, config):
        """Register all services in the container"""
        # Register configuration
        container.register_instance('config', config)

        # Register database
        from config.database_manager import DatabaseManager
        container.register_singleton(
            'database',
            lambda: DatabaseManager(config.database)
        )

        # Register analytics service
        from services.analytics_service import AnalyticsService
        container.register_singleton(
            'analytics_service',
            lambda: AnalyticsService(container.get('database'))
        )

        # Register file processor
        from services.file_processor_service import FileProcessorService
        container.register('file_processor', FileProcessorService)

    @staticmethod
    def _create_dash_app(config) -> dash.Dash:
        """Create Dash application with proper configuration"""
        import dash_bootstrap_components as dbc

        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )

        app.title = "Yōsai Intel Dashboard"

        # Configure Flask server
        app.server.config.update({
            'SECRET_KEY': config.app.secret_key,
            'DEBUG': config.app.debug,
        })

        return app

    @staticmethod
    def _register_layouts(app, container):
        """Register page layouts and callbacks"""
        from pages.main_layout import register_main_layout
        from pages.dashboard_callbacks import register_dashboard_callbacks

        register_main_layout(app)
        register_dashboard_callbacks(app, container)


def create_app() -> dash.Dash:
    """Main entry point for creating the application"""
    return AppFactory.create_app()
