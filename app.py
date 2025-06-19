# app.py - Main Application Entry Point with CSRF Fix
"""
Yōsai Intel Dashboard

This version restores the full application from ``app_backup_20250618_211158.py``
while applying the simplified CSRF workaround that proved successful in the
example file. CSRF protection via ``flask_wtf`` is disabled to avoid the
"CSRF session token is missing" error.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Any

# ---- CSRF workaround -----------------------------------------------------
# Disable CSRF checks before any Dash/Flask modules are imported
os.environ["WTF_CSRF_ENABLED"] = "False"

# ---- LazyString fix -----------------------------------------------------
# Patch json module to handle LazyString objects before any imports
import json
_original_dumps = json.dumps

def lazystring_safe_dumps(obj, **kwargs):
    def safe_default(o):
        if hasattr(o, '__class__') and 'LazyString' in str(o.__class__):
            return str(o)
        if hasattr(o, '_func') and hasattr(o, '_args'):
            try:
                return str(o)
            except Exception:
                return f"LazyString: {repr(o)}"
        if callable(o):
            return f"<function {getattr(o, '__name__', 'anonymous')}>"
        return str(o)

    if 'default' not in kwargs:
        kwargs['default'] = safe_default

    try:
        return _original_dumps(obj, **kwargs)
    except Exception:
        return _original_dumps({'error': 'Serialization failed', 'safe_repr': str(obj)[:200]})

json.dumps = lazystring_safe_dumps
# -------------------------------------------------------------------------
# Load environment variables early
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

# -------------------------------------------------------------------------
# Main application logic
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the dashboard using the YAML configuration system."""
    try:
        from core.app_factory import create_application
        from config.yaml_config import ConfigurationManager

        # Determine which configuration file to load
        config_path = get_config_path()

        # Load configuration
        config_manager = ConfigurationManager()
        config_manager.load_configuration(config_path)
        config_manager.print_startup_info()

        # Create the Dash application
        app = create_application()
        if app is None:
            print("❌ Failed to create dashboard application")
            sys.exit(1)

        # Apply CSRF workaround to the Flask server
        app.server.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY"))
        app.server.config["WTF_CSRF_ENABLED"] = False

        # Configure logging level from configuration
        app_config = config_manager.app_config
        logging.getLogger().setLevel(getattr(logging, app_config.log_level.upper()))

        # Run the application
        app.run(debug=app_config.debug, host=app_config.host, port=app_config.port)

    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"❌ Critical error: {e}")
        sys.exit(1)


def get_config_path() -> Optional[str]:
    """Select the configuration file based on environment variables."""
    from core.secret_manager import SecretManager

    manager = SecretManager()
    try:
        config_file = manager.get("YOSAI_CONFIG_FILE")
    except KeyError:
        config_file = None
    if config_file and Path(config_file).exists():
        print(f"📋 Using config file from YOSAI_CONFIG_FILE: {config_file}")
        return config_file

    env = (manager.get("YOSAI_ENV") or "development").lower()
    env_config_map = {
        "production": "config/production.yaml",
        "prod": "config/production.yaml",
        "test": "config/test.yaml",
        "testing": "config/test.yaml",
        "development": "config/config.yaml",
        "dev": "config/config.yaml",
    }
    config_path = env_config_map.get(env, "config/config.yaml")
    if Path(config_path).exists():
        print(f"📋 Using environment config: {config_path} (YOSAI_ENV={env})")
        return config_path
    print(f"⚠️  Config file not found: {config_path}, using defaults")
    return None


# -------------------------------------------------------------------------
# WSGI helpers

def get_app() -> Optional[Any]:
    """Return the Dash app instance for WSGI servers."""
    try:
        from core.app_factory import create_application
        app = create_application()
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