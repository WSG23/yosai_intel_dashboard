#!/usr/bin/env python3
"""
Complete App Factory Integration - FIXED CLASS NAMES
"""
import dash
import logging
from typing import Optional, Any
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd

# ✅ FIXED IMPORTS - Use correct config system
from config.config import get_config

logger = logging.getLogger(__name__)


def create_app() -> dash.Dash:
    """Create complete Dash application with full integration"""
    try:
        # Create Dash app with external stylesheets
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
            assets_folder='assets'
        )

        app.title = "Yōsai Intel Dashboard"

        # ✅ FIXED: Use the working config system
        config_manager = get_config()

        # ✅ FIXED: Skip plugin system for now (causing import issues)
        # We'll add this back after core functionality is working
        # plugin_manager = PluginManager(container, config_manager)
        # plugin_results = plugin_manager.load_all_plugins()
        # app._yosai_plugin_manager = plugin_manager

        # Set main layout
        app.layout = _create_main_layout()

        # Register all callbacks
        _register_global_callbacks(app)

        # Initialize services
        _initialize_services()

        logger.info("✅ Complete Dash application created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def _create_main_layout() -> html.Div:
    """Create main application layout with complete integration"""
    return html.Div([
        # URL routing component
        dcc.Location(id='url', refresh=False),

        # Navigation bar
        _create_navbar(),

        # Main content area (dynamically populated)
        html.Div(id='page-content', className="main-content p-4"),

        # Global data stores
        dcc.Store(id='global-store', data={}),
        dcc.Store(id='session-store', data={}),
        dcc.Store(id='app-state-store', data={'initial': True}),
    ])


def _create_navbar() -> dbc.Navbar:
    """Create navigation bar"""
    return dbc.Navbar([
        dbc.Container([
            # Brand
            dbc.NavbarBrand([
                html.I(className="fas fa-shield-alt me-2"),
                "Yōsai Intel Dashboard"
            ], href="/"),

            # Navigation links
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("📊 Analytics", href="/analytics")),
                dbc.NavItem(dbc.NavLink("📁 Upload", href="/upload")),
                dbc.NavItem([
                    dbc.Button(
                        "🔄 Clear Cache",
                        id="clear-cache-btn",
                        color="outline-secondary",
                        size="sm"
                    )
                ])
            ], navbar=True)
        ])
    ], color="dark", dark=True, className="mb-4")


def _create_placeholder_page(title: str, subtitle: str, message: str) -> html.Div:
    """Create placeholder page for missing modules"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(title, className="text-primary mb-3"),
                html.P(subtitle, className="text-muted mb-4"),
                dbc.Alert(message, color="warning")
            ])
        ])
    ])


@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route pages based on URL"""
    if pathname == '/analytics':
        return _get_analytics_page()
    elif pathname == '/upload':
        return _get_upload_page()
    elif pathname == '/':
        return _get_home_page()
    else:
        return html.Div([
            html.H1("Page Not Found", className="text-center mt-5"),
            html.P("The page you're looking for doesn't exist.", className="text-center"),
            dbc.Button("Go Home", href="/", color="primary", className="d-block mx-auto")
        ])


def _get_home_page() -> Any:
    """Get home page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🏯 Welcome to Yōsai Intel Dashboard", className="text-center mb-4"),
                html.P(
                    "Advanced security analytics and monitoring platform",
                    className="text-center text-muted mb-5"
                ),
                
                # Feature cards
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("📊 Analytics", className="card-title"),
                                html.P("Deep dive into security data and patterns"),
                                dbc.Button("Go to Analytics", href="/analytics", color="primary")
                            ])
                        ])
                    ], md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("📁 File Upload", className="card-title"),
                                html.P("Upload and analyze security data files"),
                                dbc.Button("Upload Files", href="/upload", color="secondary")
                            ])
                        ])
                    ], md=6)
                ])
            ])
        ])
    ])


def _get_analytics_page() -> Any:
    """Get analytics page with complete integration"""
    try:
        from pages.deep_analytics import layout
        return layout()
    except ImportError as e:
        logger.error(f"Analytics page import failed: {e}")
        return _create_placeholder_page(
            "📊 Analytics",
            "Analytics page is being loaded...",
            "The analytics module is not available. Please check the installation."
        )


def _get_upload_page() -> Any:
    """Get upload page with complete integration"""
    try:
        from pages.file_upload import layout
        return layout()
    except ImportError as e:
        logger.error(f"Upload page import failed: {e}")
        return _create_placeholder_page(
            "📁 File Upload",
            "File upload page is being loaded...",
            "The file upload module is not available. Please check the installation."
        )


def _register_global_callbacks(app: dash.Dash) -> None:
    """Register global application callbacks"""
    
    @app.callback(
        Output('global-store', 'data'),
        Input('clear-cache-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_cache(n_clicks):
        """Clear application cache"""
        if n_clicks:
            try:
                # Clear uploaded data
                from pages.file_upload import clear_uploaded_data
                clear_uploaded_data()
                logger.info("Application cache cleared")
                return {'cache_cleared': True, 'timestamp': pd.Timestamp.now().isoformat()}
            except ImportError:
                logger.warning("Could not clear uploaded data - module not available")
                return {'cache_cleared': False}
        return {}

    logger.info("✅ Global callbacks registered successfully")


def _initialize_services() -> None:
    """Initialize all application services"""
    try:
        # Initialize analytics service
        from services.analytics_service import get_analytics_service
        analytics_service = get_analytics_service()
        health = analytics_service.health_check()
        logger.info(f"Analytics service initialized: {health}")

        # Initialize configuration
        config = get_config()
        app_config = config.get_app_config()
        logger.info(f"Configuration loaded for environment: {app_config.environment}")

    except Exception as e:
        logger.warning(f"Service initialization completed with warnings: {e}")


# Export the main function
__all__ = ['create_app']