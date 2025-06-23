# app.py - Full Modular Dashboard with JSON Plugin
"""
Yōsai Intel Dashboard - Complete Implementation
Uses your existing modular architecture with JSON plugin
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Any

# ---- CSRF setup ---------------------------------------------------------
# Respect environment variable WTF_CSRF_ENABLED with secure default
os.environ.setdefault("WTF_CSRF_ENABLED", "True")

# ---- Load environment variables early ------------------------------------
try:
    from dotenv import load_dotenv
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print("✅ Loaded .env file")
    else:
        print("⚠️  .env file not found")
except ImportError:
    print("⚠️  python-dotenv not installed")

# Ensure required variables are set for development
required_vars = {
    "DB_HOST": "localhost",
    "SECRET_KEY": "change-me",
    "YOSAI_ENV": "development",
}
for var, default in required_vars.items():
    if not os.getenv(var):
        os.environ[var] = default

# ---- Main application setup ----------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_full_dashboard() -> "Dash":
    """Create the complete dashboard application with centralized callbacks"""
    try:
        from dash.dash import Dash
        import dash_bootstrap_components as dbc

        class YosaiDash(Dash):
            """Dash subclass with additional attributes for plugins."""

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self._yosai_json_plugin: Optional[Any] = None
                self._container: Optional[Any] = None
                self._component_registry: Optional[Any] = None
                self._layout_manager: Optional[Any] = None
                self._callback_registry: Optional[Any] = None

        # Load JSON plugin first
        from core.json_serialization_plugin import JsonSerializationPlugin

        json_plugin = JsonSerializationPlugin()
        json_plugin.load(None, {
            'enabled': True,
            'max_dataframe_rows': 1000,
            'auto_wrap_callbacks': True
        })
        json_plugin.configure({})
        json_plugin.start()

        logger.info("✅ JSON Serialization Plugin loaded")

        # Step 2: Create Dash app
        app = YosaiDash(
            __name__,
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                "/assets/dashboard.css"
            ],
            suppress_callback_exceptions=True,
            assets_folder="assets"
        )
        app.title = "🏯 Yōsai Intel Dashboard"

        # Apply JSON plugin to app
        json_plugin.apply_to_app(app)

        # Step 3: Initialize centralized callback registry
        from core.callback_registry import CallbackRegistry
        callback_registry = CallbackRegistry(app)

        # Step 4: Initialize component managers
        from core.component_registry import ComponentRegistry
        from core.layout_manager import LayoutManager
        from core.simple_container import get_container

        # Import component creation functions
        from components.settings_modal import create_settings_modal
        from components.settings_callback_manager import SettingsCallbackManager
        from components.door_mapping_modal import create_door_mapping_modal, DoorMappingCallbackManager
        from pages.callback_managers import AnalyticsCallbackManager
        from core.navigation_manager import NavigationCallbackManager

        # Get global container (bootstrapped separately)
        container = get_container()

        # Create your modular managers
        component_registry = ComponentRegistry()
        layout_manager = LayoutManager(component_registry)

        # Step 5: Create main layout
        main_layout = layout_manager.create_main_layout()

        if hasattr(main_layout, "children") and isinstance(main_layout.children, list):
            # Insert modals after navbar
            main_layout.children.insert(2, create_settings_modal())
            main_layout.children.insert(3, create_door_mapping_modal())

        app.layout = main_layout

        # Step 6: Register all callbacks through centralized registry

        # Register navigation callbacks (MOST IMPORTANT - this handles page switching)
        navigation_manager = NavigationCallbackManager(callback_registry, layout_manager)
        navigation_manager.register_all()

        # Register settings callbacks
        settings_manager = SettingsCallbackManager(callback_registry)
        settings_manager.register_all()

        # Register door mapping callbacks
        door_mapping_manager = DoorMappingCallbackManager(callback_registry)
        door_mapping_manager.register_all()

        # Register page-specific callbacks
        analytics_manager = AnalyticsCallbackManager(callback_registry, container)
        analytics_manager.register_all()

        # DO NOT register legacy page callbacks as they conflict
        # The file upload callbacks are handled by @callback decorators
        logger.info("All callbacks registered successfully")

        # Store references in app
        app._yosai_json_plugin = json_plugin
        app._container = container
        app._component_registry = component_registry
        app._layout_manager = layout_manager
        app._callback_registry = callback_registry

        logger.info("✅ Full dashboard created with centralized callback management")
        return app

    except Exception as e:
        logger.error(f"Failed to create full dashboard: {e}")
        raise


def main() -> None:
    """Main application entry point"""
    try:
        from core.bootstrap import bootstrap_application
        bootstrap_application()

        app = create_full_dashboard()
        if app is None:
            logger.error("Failed to create dashboard")
            sys.exit(1)

        from config.simple_config import get_config
        config = get_config()

        app.server.config["SECRET_KEY"] = config.secret_key
        app.server.config["WTF_CSRF_ENABLED"] = config.csrf_enabled

        app.run_server(
            debug=config.debug,
            host=config.host,
            port=config.port
        )

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


# -------------------------------------------------------------------------
# WSGI helpers

def get_app() -> Optional["Dash"]:
    """Return the Dash app instance for WSGI servers."""
    try:
        app = create_full_dashboard()
        if app is not None:
            app.server.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY"))
            app.server.config.setdefault("WTF_CSRF_ENABLED", os.getenv("WTF_CSRF_ENABLED", "True") == "True")
        return app
    except Exception as e:
        logger.error(f"Error creating WSGI app: {e}")
        return None


# Expose global app/server for WSGI
app = get_app()
server = app.server if app is not None else None

if __name__ == "__main__":
    main()
