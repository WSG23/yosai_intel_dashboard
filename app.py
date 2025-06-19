"""
Yōsai Intel Dashboard - Safe modular version
"""
import logging
from pathlib import Path
from core.service_registry_safe import get_safe_container
from pages import get_page_layout, register_page_callbacks
from components import create_navbar
from dashboard.layout.navbar import register_navbar_callbacks

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

        # Build page layout safely
        page_layout_fn = get_page_layout("deep_analytics")
        if page_layout_fn is not None:
            page_content = page_layout_fn()
        else:
            page_content = html.Div("Deep analytics page not available")

        # Set up basic layout including page content
        app.layout = html.Div([
            dcc.Location(id="url", refresh=False),
            create_navbar(),
            html.Div(page_content, id="page-content")
        ])

        # Register page callbacks safely
        register_page_callbacks('deep_analytics', app, container)
        register_navbar_callbacks(app)

        return app

    except Exception as e:
        logger.error(f"Error creating safe app: {e}")
        raise


if __name__ == "__main__":
    app = create_safe_app()
    app.run(debug=True, host="0.0.0.0", port=8050)

