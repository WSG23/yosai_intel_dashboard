"""
Yōsai Intel Dashboard - Safe modular version
"""
import logging
from pathlib import Path
from core.service_registry_safe import get_safe_container
from pages import get_page_layout, register_page_callbacks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_safe_app():
    """Create application with safe component loading"""
    try:
        # Get safe container
        container = get_safe_container()

        # Import Dash safely
        from dash import Dash, html, dcc
        import dash_bootstrap_components as dbc

        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        # Set up basic layout
        app.layout = html.Div([
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content")
        ])

        # Register page callbacks safely
        register_page_callbacks('deep_analytics', app, container)

        return app

    except Exception as e:
        logger.error(f"Error creating safe app: {e}")
        raise


if __name__ == "__main__":
    app = create_safe_app()
    app.run(debug=True, host="0.0.0.0", port=8050)

