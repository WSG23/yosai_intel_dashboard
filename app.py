"""
Yōsai Intel Dashboard - Safe modular version
"""
import logging
from core.service_registry_safe import get_safe_container
from core.component_registry import ComponentRegistry
from core.layout_manager import LayoutManager
from core.callback_manager import CallbackManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_safe_app():
    """Create application with safe component loading"""
    try:
        # Get safe container
        container = get_safe_container()

        # Import Dash safely
        from dash import Dash
        import dash_bootstrap_components as dbc

        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        component_registry = ComponentRegistry()
        layout_manager = LayoutManager(component_registry)
        callback_manager = CallbackManager(
            app, component_registry, layout_manager, container
        )

        # Use the old dashboard layout
        app.layout = layout_manager.create_main_layout()

        # Register all callbacks including page routing
        callback_manager.register_all_callbacks()

        return app

    except Exception as e:
        logger.error(f"Error creating safe app: {e}")
        raise


if __name__ == "__main__":
    app = create_safe_app()
    app.run(debug=True, host="0.0.0.0", port=8050)

