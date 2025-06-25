#!/usr/bin/env python3
"""
Complete App Factory Integration - Final consolidated version
Integrates all services, pages, and components
"""
import dash
import logging
from typing import Optional, Any
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd

from config.config import get_config
from core.container import Container
from core.plugins.manager import PluginManager

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

        # Initialize configuration and dependency container
        config_manager = get_config()
        container = Container()

        # Add plugin manager (from integrations/plugin_integration.txt)
        plugin_manager = PluginManager(container, config_manager)
        plugin_results = plugin_manager.load_all_plugins()
        app._yosai_plugin_manager = plugin_manager
        logger.info(f"Loaded plugins: {plugin_results}")

        # Set main layout
        app.layout = _create_main_layout()

        # Register all callbacks (this will register page-specific callbacks automatically)
        _register_global_callbacks(app)

        # Register plugin callbacks
        plugin_callback_results = plugin_manager.register_plugin_callbacks(app)
        logger.info(f"Registered plugin callbacks: {plugin_callback_results}")

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
        dcc.Store(id='app-state-store', data={'initialized': True}),
    ])


def _create_navbar() -> dbc.Navbar:
    """Create navigation bar with complete integration"""
    return dbc.Navbar([
        dbc.Container([
            # Brand with service status
            dbc.NavbarBrand([
                html.I(className="fas fa-shield-alt me-2"),
                "Yōsai Intel Dashboard",
                html.Span(id="service-status-badge", className="ms-2")
            ], href="/", className="text-primary fw-bold"),

            # Navigation links
            dbc.Nav([
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-tachometer-alt me-1"),
                    "Dashboard"
                ], href="/", active="exact")),

                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-chart-line me-1"),
                    "Analytics"
                ], href="/analytics", active="exact")),

                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-upload me-1"),
                    "Upload"
                ], href="/upload", active="exact")),

                # Service health dropdown
                dbc.DropdownMenu([
                    dbc.DropdownMenuItem("Service Health", header=True),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("View System Status", href="/health"),
                    dbc.DropdownMenuItem("Clear Cache", id="clear-cache-btn"),
                ], label="System", nav=True),

            ], className="ms-auto", navbar=True),

        ], fluid=True)
    ], color="dark", dark=True, className="mb-4")


def _register_global_callbacks(app: dash.Dash) -> None:
    """Register all global application callbacks"""

    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
        prevent_initial_call=False
    )
    def display_page(pathname: Optional[str]) -> Any:
        """Route to appropriate page with complete integration"""
        try:
            # Default to dashboard
            if pathname == "/" or pathname is None:
                return _create_dashboard_page()

            elif pathname == "/analytics":
                return _get_analytics_page()

            elif pathname == "/upload":
                return _get_upload_page()

            elif pathname == "/health":
                return _create_health_page()

            else:
                return _create_404_page(pathname)

        except Exception as e:
            logger.error(f"Error routing to {pathname}: {e}")
            return _create_error_page(f"Error loading page: {str(e)}")

    @app.callback(
        Output('service-status-badge', 'children'),
        Input('app-state-store', 'data'),
        prevent_initial_call=False
    )
    def update_service_status(app_state):
        """Update service status badge in navbar"""
        try:
            from services.analytics_service import get_analytics_service
            analytics_service = get_analytics_service()
            health = analytics_service.health_check()

            if health.get('service') == 'healthy':
                return dbc.Badge("Online", color="success", className="ms-2")
            else:
                return dbc.Badge("Issues", color="warning", className="ms-2")

        except Exception:
            return dbc.Badge("Error", color="danger", className="ms-2")

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
        from config.config import get_config
        config = get_config()
        logger.info(f"Configuration loaded for environment: {config.config.environment}")

    except Exception as e:
        logger.warning(f"Service initialization completed with warnings: {e}")


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


def _create_dashboard_page() -> dbc.Container:
    """Create main dashboard page with service integration"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("🏯 Dashboard", className="text-primary mb-4"),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Welcome to the Yōsai Intel Dashboard - Your integrated security analytics platform"
                ], color="info"),

                # Service overview cards
                html.Div(id="dashboard-service-overview")
            ])
        ]),

        # Dashboard metrics
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🚀", className="text-center text-primary mb-2"),
                        html.H5("System Online", className="text-center mb-0"),
                        html.P("All services operational", className="text-center text-muted mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📊", className="text-center text-info mb-2"),
                        html.H5("Analytics Ready", className="text-center mb-0"),
                        html.P("Data analysis available", className="text-center text-muted mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📁", className="text-center text-success mb-2"),
                        html.H5("Upload Active", className="text-center mb-0"),
                        html.P("File processing enabled", className="text-center text-muted mb-0")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🔒", className="text-center text-warning mb-2"),
                        html.H5("Security Monitor", className="text-center mb-0"),
                        html.P("Monitoring active", className="text-center text-muted mb-0")
                    ])
                ])
            ], width=3),
        ], className="mb-4"),

        # Quick actions
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🚀 Quick Actions"),
                    dbc.CardBody([
                        dbc.ButtonGroup([
                            dbc.Button([
                                html.I(className="fas fa-chart-line me-2"),
                                "Start Analytics"
                            ], href="/analytics", color="primary", size="lg"),
                            dbc.Button([
                                html.I(className="fas fa-upload me-2"),
                                "Upload Data"
                            ], href="/upload", color="secondary", size="lg"),
                            dbc.Button([
                                html.I(className="fas fa-heart me-2"),
                                "System Health"
                            ], href="/health", color="outline-info", size="lg"),
                        ])
                    ])
                ])
            ])
        ]),

        # Auto-refresh dashboard data
        dcc.Interval(id='dashboard-interval', interval=30000, n_intervals=0),  # 30 seconds

    ], fluid=True)


def _create_health_page() -> dbc.Container:
    """Create system health page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("❤️ System Health", className="text-primary mb-4"),
                html.Div(id="health-display")
            ])
        ])
    ], fluid=True)


def _create_placeholder_page(title: str, subtitle: str, message: str) -> dbc.Container:
    """Create placeholder page for missing components"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(title, className="text-primary mb-2"),
                html.P(subtitle, className="text-muted mb-4"),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    message
                ], color="info"),
                dbc.Button("← Back to Dashboard", href="/", color="primary")
            ])
        ])
    ], fluid=True)


def _create_404_page(pathname: str) -> dbc.Container:
    """Create 404 error page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("404 - Page Not Found", className="text-danger mb-4"),
                html.P(f"The page '{pathname}' was not found.", className="mb-4"),
                dbc.Alert([
                    html.P("Available pages:", className="mb-2"),
                    html.Ul([
                        html.Li(html.A("Dashboard", href="/")),
                        html.Li(html.A("Analytics", href="/analytics")),
                        html.Li(html.A("File Upload", href="/upload")),
                        html.Li(html.A("System Health", href="/health")),
                    ])
                ], color="info"),
                dbc.Button("← Back to Dashboard", href="/", color="primary")
            ])
        ])
    ], fluid=True)


def _create_error_page(error_message: str) -> dbc.Container:
    """Create error page"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("⚠️ Application Error", className="text-danger mb-4"),
                dbc.Alert([
                    html.H5("Error Details:", className="alert-heading"),
                    html.P(error_message),
                    html.Hr(),
                    html.P("Please try refreshing the page or contact support if the problem persists.", className="mb-0")
                ], color="danger"),
                dbc.Button("← Back to Dashboard", href="/", color="primary", className="mt-3")
            ])
        ])
    ], fluid=True)


# Add callback to auto-update dashboard with service data
@callback(
    Output('dashboard-service-overview', 'children'),
    Input('dashboard-interval', 'n_intervals'),
    prevent_initial_call=False
)
def update_dashboard_overview(n_intervals):
    """Update dashboard service overview"""
    try:
        from services.analytics_service import get_analytics_service
        analytics_service = get_analytics_service()
        health = analytics_service.health_check()

        # Create service status cards
        cards = []

        # Analytics Service
        service_status = health.get('service', 'unknown')
        service_color = "success" if service_status == 'healthy' else "warning"
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Analytics Service", className="card-title"),
                        dbc.Badge(service_status.title(), color=service_color)
                    ])
                ])
            ], width=4)
        )

        # Database Status
        db_status = health.get('database', 'unknown')
        db_color = "success" if db_status == 'healthy' else "warning" if db_status == 'not_configured' else "danger"
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Database", className="card-title"),
                        dbc.Badge(db_status.replace('_', ' ').title(), color=db_color)
                    ])
                ])
            ], width=4)
        )

        # File Upload Status
        uploaded_files = health.get('uploaded_files', 0)
        file_color = "success" if isinstance(uploaded_files, int) and uploaded_files > 0 else "secondary"
        file_text = f"{uploaded_files} files" if isinstance(uploaded_files, int) else "Available"
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Uploaded Files", className="card-title"),
                        dbc.Badge(file_text, color=file_color)
                    ])
                ])
            ], width=4)
        )

        return dbc.Row(cards, className="mb-4")

    except Exception as e:
        logger.error(f"Error updating dashboard overview: {e}")
        return dbc.Alert("Service overview unavailable", color="warning", className="mb-4")


# Add health page callback
@callback(
    Output('health-display', 'children'),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def update_health_display(pathname):
    """Update health display when health page is visited"""
    if pathname != '/health':
        return html.Div()

    try:
        from services.analytics_service import get_analytics_service
        analytics_service = get_analytics_service()
        health = analytics_service.health_check()

        components = []

        # Overall status
        overall_status = "Healthy" if health.get('service') == 'healthy' else "Issues Detected"
        overall_color = "success" if health.get('service') == 'healthy' else "warning"

        components.append(
            dbc.Alert([
                html.H4(f"Overall Status: {overall_status}", className="alert-heading"),
                html.P(f"Last checked: {health.get('timestamp', 'Unknown')}")
            ], color=overall_color, className="mb-4")
        )

        # Service details
        components.append(
            dbc.Card([
                dbc.CardHeader("Service Details"),
                dbc.CardBody([
                    html.Dl([
                        html.Dt("Analytics Service:"),
                        html.Dd(health.get('service', 'Unknown')),
                        html.Dt("Database:"),
                        html.Dd(health.get('database', 'Unknown')),
                        html.Dt("Uploaded Files:"),
                        html.Dd(str(health.get('uploaded_files', 'Unknown'))),
                        html.Dt("Configuration:"),
                        html.Dd("Loaded" if health else "Error"),
                    ])
                ])
            ])
        )

        return components

    except Exception as e:
        return dbc.Alert(f"Health check failed: {str(e)}", color="danger")


# Export main function
__all__ = ['create_app']
