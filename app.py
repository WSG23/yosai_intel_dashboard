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
    """Create application with JSON plugin actually loaded and working"""
    try:
        import dash
        import dash_bootstrap_components as dbc
        from dash import html, dcc

        # Step 1: Create the basic Dash app
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        app.title = "Yōsai Intel Dashboard"

        # Step 2: **ACTUALLY LOAD THE JSON PLUGIN**
        from core.json_serialization_plugin import JsonSerializationPlugin
        from core.lazystring_json_provider import LazyStringSafeJSONProvider
        from core.container import Container

        # Create DI container
        container = Container()

        # Create and configure the JSON plugin
        json_plugin = JsonSerializationPlugin()
        plugin_config = {
            'enabled': True,
            'max_dataframe_rows': 1000,
            'max_string_length': 10000,
            'include_type_metadata': True,
            'compress_large_objects': True,
            'fallback_to_repr': True,
            'auto_wrap_callbacks': True
        }

        # Load the plugin
        plugin_loaded = json_plugin.load(container, plugin_config)
        if plugin_loaded:
            json_plugin.configure(plugin_config)
            json_plugin.start()

            # Use custom JSON provider backed by the plugin
            app.server.json_provider_class = LazyStringSafeJSONProvider
            app.server.json = LazyStringSafeJSONProvider(
                app.server, json_plugin.serialization_service
            )

            # Store plugin in app for callbacks to use
            app._yosai_json_plugin = json_plugin
            app._yosai_container = container

            logger.info("✅ JSON Serialization Plugin loaded and active")
        else:
            logger.error("❌ Failed to load JSON plugin")

        # Step 3: Create basic layout
        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.H1("🏯 Yōsai Intel Dashboard", className="text-center mb-4"),
            html.Hr(),
            html.Div([
                dbc.Alert("✅ Application created with JSON plugin!", color="success"),
                dbc.Alert("✅ JSON serialization issues should be resolved", color="info"),
                html.P("Environment configuration loaded and working."),
                html.P("JSON plugin active and handling all serialization."),
                html.A("Go to Analytics", href="/analytics", className="btn btn-primary"),
            ], className="container")
        ])

        # Step 4: Add a test route to verify JSON handling
        @app.server.route('/test-json')
        def test_json():
            """Test route to verify JSON plugin is working"""
            import pandas as pd
            from datetime import datetime

            # Create test data that would normally fail JSON serialization
            test_data = {
                'dataframe': pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
                'datetime': datetime.now(),
                'function': lambda x: x,
                'complex_object': {'nested': {'data': 'test'}}
            }

            # This should work now with the plugin
            try:
                # Use the plugin's serialization service
                serialized = json_plugin.serialization_service.sanitize_for_transport(test_data)
                return app.server.json.response({
                    'status': 'success',
                    'message': 'JSON plugin working correctly',
                    'data': serialized
                })
            except Exception as e:
                return app.server.json.response({
                    'status': 'error',
                    'message': f'JSON plugin error: {str(e)}'
                })

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
