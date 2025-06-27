"""
Complete App Factory Integration - FIXED CALLBACK REGISTRATION
"""
import dash
import logging
from typing import Optional, Any
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd

# FIXED IMPORTS - Use correct config system
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
            assets_folder="assets",
        )

        app.title = "Yōsai Intel Dashboard"

        # FIXED: Use the working config system
        config_manager = get_config()

        # Set main layout
        app.layout = _create_main_layout()

        # FIXED: Register all callbacks INCLUDING page callbacks
        _register_all_callbacks(app)

        # Initialize services
        _initialize_services()

        logger.info("✅ Complete Dash application created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def _create_main_layout() -> html.Div:
    """Create main application layout with proper routing"""
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            _create_navbar(),
            html.Div(id="page-content"),
            dcc.Store(id="global-store", data={}),
        ]
    )



def _create_navbar() -> dbc.Navbar:
    """Create navigation bar"""
    return dbc.Navbar(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.A(
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    html.H4(
                                                        "Yōsai Intel Dashboard",
                                                        className="mb-0 text-white",
                                                    )
                                                ),
                                            ],
                                            align="center",
                                        ),
                                        href="/",
                                        style={"textDecoration": "none"},
                                    )
                                ]
                            ),
                            dbc.Col(
                                [
                                    dbc.Nav(
                                        [
                                            dbc.NavItem(
                                                dbc.NavLink("Home", href="/", active="exact")
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Analytics",
                                                    href="/analytics",
                                                    active="exact"
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Upload",
                                                    href="/upload",
                                                    active="exact"
                                                )
                                            ),
                                        ],
                                        pills=True,
                                    )
                                ],
                                width="auto",
                            ),
                        ],
                        align="center",
                    ),
                ]
            )
        ],
        color="dark",
        dark=True,
        className="mb-4",
    )


def _create_placeholder_page(title: str, subtitle: str, message: str) -> html.Div:
    """Create placeholder page for missing modules"""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(title, className="text-primary mb-3"),
                            html.P(subtitle, className="text-muted mb-4"),
                            dbc.Alert(message, color="warning"),
                        ]
                    )
                ]
            )
        ]
    )


def _get_home_page() -> html.Div:
    """Get home/dashboard page"""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("Yōsai Intel Dashboard", className="text-primary mb-4"),
                            html.P(
                                "Advanced security analytics and data intelligence platform",
                                className="lead text-muted mb-4",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "📊 Analytics",
                                                                className="card-title",
                                                            ),
                                                            html.P(
                                                                "Explore security patterns and insights"
                                                            ),
                                                            dbc.Button(
                                                                "View Analytics",
                                                                href="/analytics",
                                                                color="primary",
                                                            ),
                                                        ]
                                                    )
                                                ]
                                            )
                                        ],
                                        md=6,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardBody(
                                                        [
                                                            html.H4(
                                                                "📁 Upload",
                                                                className="card-title",
                                                            ),
                                                            html.P(
                                                                "Upload and analyze security data files"
                                                            ),
                                                            dbc.Button(
                                                                "Upload Files",
                                                                href="/upload",
                                                                color="secondary",
                                                            ),
                                                        ]
                                                    )
                                                ]
                                            )
                                        ],
                                        md=6,
                                    ),
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    )


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
            "The analytics module is not available. Please check the installation.",
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
            "The file upload module is not available. Please check the installation.",
        )


@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    """Route pages based on URL"""
    if pathname == "/analytics":
        return _get_analytics_page()
    elif pathname == "/upload" or pathname == "/file-upload":  # Handle both paths
        return _get_upload_page()
    elif pathname == "/":
        return _get_home_page()
    else:
        return html.Div(
            [
                html.H1("Page Not Found", className="text-center mt-5"),
                html.P(
                    "The page you're looking for doesn't exist.",
                    className="text-center text-muted",
                ),
                dbc.Button("Go Home", href="/", color="primary", className="mt-3"),
            ],
            className="text-center",
        )


def _register_all_callbacks(app: dash.Dash) -> None:
    """FIXED: Register ALL callbacks including page callbacks"""
    
    # Register global callbacks first
    _register_global_callbacks(app)
    
    # CRITICAL FIX: Import page modules to register their callbacks
    try:
        logger.info("Registering page callbacks...")
        
        # Import file_upload module to register its callbacks
        import pages.file_upload
        logger.info("✅ File upload callbacks registered")
        
        # Import analytics callbacks if available
        try:
            import pages.deep_analytics_callbacks
            logger.info("✅ Analytics callbacks registered")
        except ImportError:
            logger.warning("Analytics callbacks not available")
            
    except ImportError as e:
        logger.error(f"Failed to register page callbacks: {e}")
    
    logger.info("✅ All callbacks registered successfully")


def _register_global_callbacks(app: dash.Dash) -> None:
    """Register global application callbacks"""

    @app.callback(
        Output("global-store", "data"),
        Input("clear-cache-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_cache(n_clicks):
        """Clear application cache"""
        if n_clicks:
            try:
                # Clear uploaded data
                from pages.file_upload import clear_uploaded_data
                clear_uploaded_data()
                logger.info("Application cache cleared")
                return {
                    "cache_cleared": True,
                    "timestamp": pd.Timestamp.now().isoformat(),
                }
            except ImportError:
                logger.warning("Could not clear uploaded data - module not available")
                return {"cache_cleared": False}
        return {}

    # Register device learning callbacks
    try:
        from services.device_learning_service import create_learning_callbacks
        create_learning_callbacks()
        logger.info("✅ Device learning callbacks registered")
    except ImportError as e:
        logger.warning(f"Device learning callbacks not available: {e}")

    # Execute upload page callbacks via module import
    import pages.file_upload  # This executes the @callback decorators

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
__all__ = ["create_app"]
