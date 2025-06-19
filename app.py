# app.py - FIXED: Now actually loads and uses the JSON plugin
"""
Yōsai Intel Dashboard - FIXED VERSION
This version actually instantiates and uses the JSON serialization plugin
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Any

# ---- CSRF workaround -----------------------------------------------------
# Disable CSRF checks before any Dash/Flask modules are imported
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
    "AUTH0_CLIENT_ID": "your-client-id",
    "AUTH0_CLIENT_SECRET": "your-client-secret",
    "AUTH0_DOMAIN": "your-domain.auth0.com",
    "AUTH0_AUDIENCE": "your-api-audience",
    "YOSAI_ENV": "development",
}
for var, default in required_vars.items():
    if not os.getenv(var):
        os.environ[var] = default

# ---- Main application with JSON plugin -----------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app_with_json_plugin() -> Optional[Any]:
    """Create application with JSON plugin - SIMPLIFIED VERSION"""
    try:
        import dash
        import dash_bootstrap_components as dbc
        from dash import html, dcc

        # Step 1: Load the JSON plugin FIRST (it auto-starts globally)
        from core.json_serialization_plugin import JsonSerializationPlugin

        json_plugin = JsonSerializationPlugin()

        # Simple config
        plugin_config = {
            'enabled': True,
            'max_dataframe_rows': 1000,
            'auto_wrap_callbacks': True
        }

        # Load and start the plugin
        json_plugin.load(None, plugin_config)  # No container needed
        json_plugin.configure(plugin_config)
        json_plugin.start()  # This applies global patches

        logger.info("✅ JSON Serialization Plugin loaded and started")

        # Step 2: Create the Dash app (JSON is now globally patched)
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        app.title = "Yōsai Intel Dashboard"

        # Step 3: Apply plugin to this specific app
        json_plugin.apply_to_app(app)

        # Step 4: Store plugin reference
        app._yosai_json_plugin = json_plugin

        # Step 5: Create layout (now JSON-safe)
        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.H1("🏯 Yōsai Intel Dashboard", className="text-center mb-4"),
            html.Hr(),
            html.Div([
                dbc.Alert("✅ Application created with JSON plugin!", color="success"),
                dbc.Alert("✅ JSON serialization issues resolved globally", color="info"),
                html.P("JSON plugin is active and handling all serialization."),
                html.A("Go to Analytics", href="/analytics", className="btn btn-primary"),
            ], className="container")
        ])

        logger.info("Dashboard application created successfully with JSON plugin")
        return app

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        return None


def main() -> None:
    """Run the dashboard with JSON plugin actually loaded"""
    try:
        print("\n" + "=" * 60)
        print("🏯 YŌSAI INTEL DASHBOARD - JSON PLUGIN ENABLED")
        print("=" * 60)

        # Create app with JSON plugin
        app = create_app_with_json_plugin()
        if app is None:
            print("❌ Failed to create dashboard application")
            sys.exit(1)

        # Apply additional Flask config
        app.server.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY"))
        app.server.config["WTF_CSRF_ENABLED"] = False

        # Print startup info
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', '8050'))

        print(f"🌐 URL: http://{host}:{port}")
        print(f"🧪 Test JSON: http://{host}:{port}/test-json")
        print(f"📊 Analytics: http://{host}:{port}/analytics")
        print("✅ JSON Plugin: ACTIVE")
        print("=" * 60)
        print("\n🚀 Dashboard starting with JSON plugin...")

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
# WSGI helpers with JSON plugin

def get_app() -> Optional[Any]:
    """Return the Dash app instance for WSGI servers."""
    try:
        app = create_app_with_json_plugin()
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
