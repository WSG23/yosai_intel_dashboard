"""
App factory with proper JSON plugin integration
"""

from typing import Any, Optional
import logging
import dash
from flask_login import login_required
from flask_wtf import CSRFProtect
from flask import session, redirect, request

# Import Babel safely
try:
    from flask_babel import Babel, lazy_gettext as _lazy_gettext

    BABEL_AVAILABLE = True

    def lazy_gettext(text: str) -> str:
        """Get translated text as regular string (not LazyString)"""
        result = _lazy_gettext(text)
        return str(result)  # Force conversion to prevent JSON issues

except ImportError:
    BABEL_AVAILABLE = False

    def lazy_gettext(text: str) -> str:
        return str(text)

    class Babel:
        def __init__(self, app=None) -> None:
            pass

        def init_app(self, app) -> None:
            pass


from .auth import init_auth
from config.yaml_config import get_configuration_manager
from core.plugins.config import get_service_locator
from .component_registry import ComponentRegistry
from .layout_manager import LayoutManager
from .callback_manager import CallbackManager
from .service_registry import get_configured_container_with_yaml
from .container import Container

logger = logging.getLogger(__name__)


class YosaiDash(dash.Dash):
    """Enhanced Dash subclass with YAML configuration and DI container"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._yosai_container: Optional[Container] = None
        self._config_manager: Optional['ConfigurationManager'] = None
        self._yosai_plugin_manager: Optional[Any] = None


class DashAppFactory:
    """Factory for creating Dash applications with YAML configuration and JSON plugin"""

    @staticmethod
    def create_app(
        config_manager: Optional['ConfigurationManager'] = None,
    ) -> Optional[YosaiDash]:
        """Create and configure a Dash app with proper JSON plugin integration"""

        try:
            # Create or get configuration manager
            if config_manager is None:
                config_manager = get_configuration_manager()

            # Create DI container with YAML configuration
            container = get_configured_container_with_yaml(config_manager)

            # CRITICAL: Load and start JSON plugin EARLY
            from core.json_serialization_plugin import JsonSerializationPlugin

            json_plugin = JsonSerializationPlugin()
            plugin_config = {
                "enabled": True,
                "max_dataframe_rows": 1000,
                "max_string_length": 10000,
                "include_type_metadata": True,
                "compress_large_objects": True,
                "fallback_to_repr": True,
                "auto_wrap_callbacks": True,
            }

            # Load, configure, and start the plugin
            plugin_loaded = json_plugin.load(container, plugin_config)
            if plugin_loaded:
                json_plugin.configure(plugin_config)
                json_plugin.start()  # This applies global JSON patches
                logger.info("✅ JSON Serialization Plugin loaded and started")
            else:
                logger.error("❌ Failed to load JSON plugin")

            # Create Dash app with configuration
            app = YosaiDash(
                __name__,
                external_stylesheets=DashAppFactory._get_stylesheets(config_manager),
                suppress_callback_exceptions=True,
                meta_tags=DashAppFactory._get_meta_tags(config_manager),
            )

            app.title = config_manager.app_config.title
            server = app.server

            # Store plugin and container references in app
            app._config_manager = config_manager
            app._yosai_container = container
            app._yosai_json_plugin = json_plugin

            # Create plugin manager and load other plugins
            try:
                from core.plugins.manager import PluginManager

                plugin_manager = PluginManager(container, config_manager)
                plugin_results = plugin_manager.load_all_plugins()
                app._yosai_plugin_manager = plugin_manager
                logger.info(f"Loaded additional plugins: {plugin_results}")
            except Exception as e:
                logger.warning(f"Plugin manager initialization failed: {e}")

            # Initialize components
            component_registry = ComponentRegistry()
            layout_manager = LayoutManager(component_registry)
            callback_manager = CallbackManager(
                app, component_registry, layout_manager, container
            )

            # Set layout
            app.layout = layout_manager.create_main_layout()

            # Register callbacks
            callback_manager.register_all_callbacks()

            # Register plugin callbacks if plugin manager is available
            if hasattr(app, "_yosai_plugin_manager"):
                try:
                    plugin_callback_results = (
                        app._yosai_plugin_manager.register_plugin_callbacks(app)
                    )
                    logger.info(
                        f"Registered plugin callbacks: {plugin_callback_results}"
                    )
                except Exception as e:
                    logger.warning(f"Plugin callback registration failed: {e}")

            # Configure Flask server
            server.config.update(
                SECRET_KEY=config_manager.security_config.secret_key,
                SESSION_COOKIE_SECURE=True,
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE="Strict",
            )

            # Initialize auth and other Flask extensions
            try:
                CSRFProtect(server)
                init_auth(server)
            except Exception as e:
                logger.warning(f"Auth initialization failed: {e}")

            # Safely wrap dash.index with login_required
            try:
                if "dash.index" in server.view_functions:
                    server.view_functions["dash.index"] = login_required(
                        server.view_functions["dash.index"]
                    )
            except Exception as e:
                logger.warning(f"Could not wrap dash.index with login_required: {e}")

            # Initialize Babel for internationalization
            if BABEL_AVAILABLE:
                babel = Babel(server)

                def _select_locale() -> str:
                    return session.get("lang", "en")

                if hasattr(babel, "localeselector"):

                    @babel.localeselector
                    def get_locale() -> str:
                        return _select_locale()

                else:
                    babel.locale_selector_func = _select_locale

                @server.route("/i18n/<lang>")
                def set_lang(lang: str):
                    session["lang"] = lang
                    return redirect(request.referrer or "/")

            # Add JSON plugin health check endpoint
            @server.route("/health/json-plugin")
            def json_plugin_health():
                """Health check endpoint for JSON plugin"""
                if hasattr(app, "_yosai_json_plugin"):
                    health = app._yosai_json_plugin.health_check()
                    # Use our safe JSON serialization
                    from flask import Response
                    import json

                    return Response(json.dumps(health), mimetype="application/json")
                else:
                    return Response(
                        '{"error": "JSON plugin not available"}',
                        mimetype="application/json",
                    )

            logger.info(
                "✅ Dashboard application created successfully with JSON plugin"
            )
            return app

        except ImportError as e:
            logger.error(f"Cannot create app - missing dependencies: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create Dash application: {e}")
            return None

    @staticmethod
    def _get_stylesheets(config_manager: 'ConfigurationManager') -> list:
        """Get CSS stylesheets based on configuration"""
        stylesheets = ["/assets/css/main.css"]

        try:
            import dash_bootstrap_components as dbc

            if hasattr(dbc, "themes") and hasattr(dbc.themes, "BOOTSTRAP"):
                stylesheets.insert(0, dbc.themes.BOOTSTRAP)
        except ImportError:
            pass

        return stylesheets

    @staticmethod
    def _get_meta_tags(config_manager: 'ConfigurationManager') -> list:
        """Get HTML meta tags based on configuration"""
        return [
            {"name": "viewport", "content": "width=device-width, initial-scale=1"},
            {"name": "theme-color", "content": "#1B2A47"},
            {"name": "description", "content": "Yōsai Intel Security Dashboard"},
            {"name": "application-name", "content": config_manager.app_config.title},
        ]


def create_application(config_path: Optional[str] = None) -> Optional[YosaiDash]:
    """Create application with enhanced modular configuration"""
    try:
        # Load configuration
        config_manager = get_configuration_manager()
        if config_path:
            config_manager.load_configuration(config_path)
        else:
            config_manager.load_configuration()

        # Initialize modular services
        service_locator = get_service_locator()
        service_locator.initialize_from_config(config_manager)
        service_locator.start_services()

        app = DashAppFactory.create_app(config_manager)

        if app is None:
            logger.error("Failed to create Dash app instance")
            return None

        # Store service locator in app for later access
        app._yosai_service_locator = service_locator

        logger.info("Dashboard application created successfully with modular configuration")
        return app

    except ImportError:
        logger.error("Cannot create application - Dash dependencies not available")
        print("❌ Error: Dash not installed. Run: pip install dash dash-bootstrap-components")
        return None
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        return None


def create_application_for_testing() -> Optional[YosaiDash]:
    """Create application instance configured for unit tests."""
    try:
        app = create_application(None)
        if app is None:
            return None

        server = app.server

        @server.route("/api/ping")
        def ping() -> Any:
            from flask import Response
            import json

            # This will use our patched JSON handling
            return Response(
                json.dumps({"msg": lazy_gettext("pong")}), mimetype="application/json"
            )

        return app
    except Exception as e:
        logger.error(f"Error creating test application: {e}")
        return None


# Export main functions
__all__ = [
    "create_application",
    "create_application_for_testing",
    "DashAppFactory",
    "YosaiDash",
]
