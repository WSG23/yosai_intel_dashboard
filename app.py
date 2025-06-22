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

# ---- CSRF workaround -----------------------------------------------------
os.environ["WTF_CSRF_ENABLED"] = "False"

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
    "SECRET_KEY": "dev-secret-change-in-production-12345",
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


def create_full_dashboard():
    """Create the complete dashboard application with centralized callbacks"""
    try:
        import dash
        import dash_bootstrap_components as dbc

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
        app = dash.Dash(
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
        from core.container import Container

        # Import component creation functions
        from components.settings_modal import create_settings_modal
        from components.settings_callback_manager import SettingsCallbackManager
        from components.door_mapping_modal import create_door_mapping_modal, DoorMappingCallbackManager
        from pages.callback_managers import AnalyticsCallbackManager, FileUploadCallbackManager
        from core.navigation_manager import NavigationCallbackManager

        # Create container for dependency injection
        container = Container()

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

        file_upload_manager = FileUploadCallbackManager(callback_registry, container)
        file_upload_manager.register_all()

        # Register legacy page callbacks until fully migrated
        try:
            from pages import register_page_callbacks
            register_page_callbacks('deep_analytics', app, container)
            register_page_callbacks('file_upload', app, container)
        except Exception as e:
            logger.warning(f"Legacy page callback registration failed: {e}")

        # Store references in app
        app._yosai_json_plugin = json_plugin
        app._yosai_container = container
        app._component_registry = component_registry
        app._layout_manager = layout_manager
        app._callback_registry = callback_registry

        logger.info("✅ Full dashboard created with centralized callback management")
        return app

    except Exception as e:
        logger.error(f"Failed to create full dashboard: {e}")
        raise


def main() -> None:
    """Run the full dashboard"""
    try:
        print("\n" + "=" * 60)
        print("🏯 YŌSAI INTEL DASHBOARD - FULL VERSION")
        print("=" * 60)

        # Create full dashboard
        app = create_full_dashboard()
        if app is None:
            print("❌ Failed to create dashboard application")
            sys.exit(1)

        # Apply Flask config
        app.server.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY"))
        app.server.config["WTF_CSRF_ENABLED"] = False

        # Print startup info
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', '8050'))

        print(f"🌐 URL: http://{host}:{port}")
        print(f"📊 Analytics: http://{host}:{port}/analytics")
        print("✅ JSON Plugin: ACTIVE")
        print("✅ Modular Architecture: LOADED")
        print("=" * 60)
        print("\n🚀 Full dashboard starting...")

        # Run the application
        app.run(debug=True, host=host, port=port)

    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)


# -------------------------------------------------------------------------
# WSGI helpers

def get_app() -> Optional[Any]:
    """Return the Dash app instance for WSGI servers."""
    try:
        app = create_full_dashboard()
        if app:
            app.server.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY"))
            app.server.config["WTF_CSRF_ENABLED"] = False
        return app
    except Exception as e:
        logger.error(f"Error creating WSGI app: {e}")
        return None


# Expose global app/server for WSGI
app = get_app()
server = app.server if app is not None else None

if __name__ == "__main__":
    main()
