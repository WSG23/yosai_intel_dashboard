"""
Working app factory without unified config dependencies
"""
import dash
import logging
from typing import Optional
import dash_bootstrap_components as dbc
from dash import html, dcc

logger = logging.getLogger(__name__)

def create_app() -> dash.Dash:
    """Create a working Dash application"""
    try:
        # Create basic Dash app
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        
        app.title = "Yōsai Intel Dashboard"
        
        # Basic layout to verify app works
        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.H1("🏯 Yōsai Intel Dashboard", className="text-center"),
            html.Hr(),
            html.Div([
                dbc.Alert("✅ Application started successfully!", color="success"),
                dbc.Alert("🔧 Using temporary app factory", color="info"),
                html.P("Ready for development."),
            ], className="container")
        ])
        
        logger.info("✅ Dash application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise

def create_application():
    """Legacy compatibility function"""
    return create_app()
