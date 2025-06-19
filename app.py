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


def create_full_dashboard() -> Optional[Any]:
    """Create full dashboard with your modular architecture"""
    try:
        import dash
        import dash_bootstrap_components as dbc
        from dash import html, dcc

        # Step 1: Load JSON plugin first
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
                "/assets/dashboard.css"  # Your custom CSS
            ],
            suppress_callback_exceptions=True,
            assets_folder="assets"
        )
        app.title = "🏯 Yōsai Intel Dashboard"
        
        # Apply JSON plugin to app
        json_plugin.apply_to_app(app)

        # Step 3: Initialize your modular components
        from core.component_registry import ComponentRegistry
        from core.layout_manager import LayoutManager
        from core.callback_manager import CallbackManager
        from core.container import Container

        # Create container for dependency injection
        container = Container()
        
        # Create your modular managers
        component_registry = ComponentRegistry()
        layout_manager = LayoutManager(component_registry)
        callback_manager = CallbackManager(app, component_registry, layout_manager, container)

        # Step 4: Create main layout using your layout manager
        app.layout = layout_manager.create_main_layout()

        # Step 5: Register all callbacks using your callback manager
        callback_manager.register_all_callbacks()

        # Store references in app
        app._yosai_json_plugin = json_plugin
        app._yosai_container = container
        app._component_registry = component_registry
        app._layout_manager = layout_manager
        app._callback_manager = callback_manager

        logger.info("✅ Full dashboard created with modular architecture")
        return app

    except Exception as e:
        logger.error(f"Failed to create full dashboard: {e}")
        import traceback
        traceback.print_exc()
        return None


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
